from app.reports import policy_brief


def test_build_brief_has_expected_shape(data_df, countries_df):
    brief = policy_brief.build_brief(data_df, countries_df, "IT.NET.USER.ZS", top_n=5, years_back=10)

    assert brief["indicator_code"] == "IT.NET.USER.ZS"
    assert len(brief["ranking"]) == 5
    assert len(brief["improvers"]) <= 5
    assert len(brief["narrative"]) >= 3


def test_build_brief_rejects_unknown_indicator(data_df, countries_df):
    import pytest

    with pytest.raises(ValueError):
        policy_brief.build_brief(data_df, countries_df, "NOT.A.REAL.CODE")


def test_render_markdown_contains_key_sections(data_df, countries_df):
    brief = policy_brief.build_brief(data_df, countries_df, "IT.NET.USER.ZS")
    md = policy_brief.render_markdown(brief)

    assert md.startswith("# Policy Brief")
    assert "## Summary" in md
    assert "## Digital readiness landscape" in md
    assert brief["ranking"].iloc[0]["name"] in md


def test_render_pdf_produces_valid_pdf_bytes(data_df, countries_df):
    brief = policy_brief.build_brief(data_df, countries_df, "IT.NET.USER.ZS", top_n=3)
    pdf_bytes = policy_brief.render_pdf(brief)

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000
