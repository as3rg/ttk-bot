import base64
from io import BytesIO

import requests

# todo max image size = 1 MB. Compress
# todo max pixel size 20Mpx. Downgrade
# todo fix max 1
MAX_FILE_COUNT = 1
YC_URL = "https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze"


def _to_content(img):
    buffered = BytesIO()
    img.save(buffered, format=img.format)
    return buffered.getvalue()


def _encode_file(content):
    return base64.b64encode(content).decode("utf-8")


def _get_data(imgs, folder_id, iam):
    assert len(imgs) <= MAX_FILE_COUNT
    headers = {
        "Authorization": f"Bearer {iam}"
    }
    data = {
        "folderId": folder_id,
        "analyze_specs": []
    }
    for img in imgs:
        data['analyze_specs'].append({
            "content": _encode_file(_to_content(img)),
            "features": [{
                "type": "TEXT_DETECTION",
                "text_detection_config": {
                    "language_codes": ["ru", "en"]
                }
            }]
        })

    res = requests.post(YC_URL, json=data, headers=headers)
    if res.status_code != 200:
        raise RuntimeError(f"Error connecting to YaCloud(code {res.status_code}): {res.text}")
    return res.json()


def _merge_words(line, word_sep=" "):
    line["text"] = word_sep.join(word["text"] for word in line["words"])


def _merge_lines(block, word_sep=" ", line_sep="\n"):
    for line in block["lines"]:
        _merge_words(line, word_sep)
    block["text"] = line_sep.join(line["text"] for line in block["lines"])


def _parse_data(data, word_sep=" ", line_sep="\n"):
    if "results" not in data:
        return None

    def process_result(analyze_results):
        analyze_results_results = analyze_results.get("results", [])
        assert len(analyze_results_results) <= 1, "Single feature's analyze result was expected"
        analyze_results_results_0 = analyze_results_results[0] if analyze_results_results else {}
        text_detection = analyze_results_results_0.get("textDetection", {})
        pages = text_detection.get("pages", [])
        assert len(pages) <= 1, f"Only one page files are supported. {len(pages)} pages found"
        page_0 = pages[0] if pages else {}
        blocks = page_0.get("blocks", [])
        for block in blocks:
            _merge_lines(block, word_sep, line_sep)
        return page_0.get("blocks", [])

    return [process_result(analyze_result) for analyze_result in data["results"]]


def parse(imgs, folder_id, iam, word_sep=" ", line_sep="\n"):
    data = _get_data(imgs, folder_id, iam)
    result = _parse_data(data, word_sep, line_sep)
    if result is None:
        result = [[]] * len(imgs)
    return result
