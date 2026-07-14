from src.main import extract_daily_report_content


def test_extract_daily_report_content_with_colon():
    result = extract_daily_report_content("生成日报：今天完成了接口测试")

    assert result == "今天完成了接口测试"


def test_extract_daily_report_content_without_colon():
    result = extract_daily_report_content("生成日报 今天完成了接口测试")

    assert result == "今天完成了接口测试"


def test_extract_daily_report_content_with_other_prefix():
    result = extract_daily_report_content("帮我写日报：今天调试了 OpenClaw")

    assert result == "今天调试了 OpenClaw"


def test_extract_daily_report_content_only_command():
    result = extract_daily_report_content("生成日报")

    assert result == ""


def test_extract_daily_report_content_unknown_intent():
    result = extract_daily_report_content("你好")

    assert result is None