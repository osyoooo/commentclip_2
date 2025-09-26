# app.py
# ------------------------------------------------------------
# コメントクリップ（HTMLメール）ジェネレーター（Streamlit）
# - 週次で変更する箇所をフォーム入力し、HTMLを自動生成
# - 任意件数のコメンテーター（カード）に対応
# - CSV一括入力にも対応
# - モノグラム正円表示対応
# ------------------------------------------------------------

from __future__ import annotations

import re
import html
from datetime import date
from typing import List, Dict, Optional

import streamlit as st
from streamlit.components.v1 import html as st_html


# =========================
# ユーティリティ
# =========================
def escape_nl2br(text: str) -> str:
    """HTMLエスケープ + 改行を <br> に変換"""
    if text is None:
        return ""
    return html.escape(text).replace("\n", "<br>")


def auto_monogram(full_name: str) -> str:
    """
    氏名からモノグラム（丸アイコンに表示する1文字）を自動抽出。
    ルール：
      - スペース（半角/全角）で姓・名を分解し、最初のトークンの先頭1文字
      - 分解できない場合は文字列の先頭1文字
    """
    if not full_name:
        return "名"
    # 全角スペースも考慮
    tokens = re.split(r"[ \u3000]+", full_name.strip())
    if tokens and tokens[0]:
        return tokens[0][0]
    return full_name.strip()[0]


def format_delivery_date(d: date, style: str) -> str:
    """
    配信日の表記を生成。
    style:
      - "MD": "📅 9月1日配信号"
      - "YMD": "📅 2025年9月1日配信号"
    """
    if style == "YMD":
        return f"📅 {d.year}年{d.month}月{d.day}日配信号"
    return f"📅 {d.month}月{d.day}日配信号"


def color_cycle(idx: int) -> str:
    """
    カード上部ストリップ色の既定サイクル。
    サンプルの配色（#c7d2fe / #a5b4fc）を交互に。
    """
    palette = ["#c7d2fe", "#a5b4fc"]
    return palette[idx % len(palette)]


# =========================
# HTMLレンダリング
# =========================
def render_card(
    idx: int,
    issue_label: str,
    article_title: str,
    comment_text: str,
    commenter_name: str,
    commenter_org: str,
    link_url: str,
    strip_color: str,
    monogram: Optional[str] = None,
    comment_bar_color: str = "#2563eb",
) -> str:
    """
    1枚のカード（記事＋コメント）HTMLを返す。
    元テンプレートの構造を尊重しつつ、可変部分を差し込み。
    """
    # フィールド整形
    _issue_label = escape_nl2br(issue_label)
    _article_title = escape_nl2br(article_title)
    _comment_text = escape_nl2br(comment_text)
    _commenter_name = escape_nl2br(commenter_name)
    _commenter_org = escape_nl2br(commenter_org)
    _link_url = (link_url or f"#article{idx+1}").strip()
    _strip_color = strip_color or color_cycle(idx)
    _mono = (monogram or auto_monogram(commenter_name)).strip()[:1] or "名"

    card_html = f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;">
      <tbody>
        <tr><td style="height:4px;background:{_strip_color};border-top-left-radius:12px;border-top-right-radius:12px;"></td></tr>
        <tr>
          <td style="padding:18px 20px 8px 20px;">
            <table role="presentation" width="100%">
              <tbody><tr>
                <td style="white-space:nowrap;color:#475569;font:600 13px/1.4 Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;padding-right:10px;vertical-align:bottom;">{_issue_label}</td>
                <td style="color:#0f172a;font:700 19px/1.4 Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;">{_article_title}</td>
              </tr></tbody>
            </table>
          </td>
        </tr>
        <tr><td style="padding:6px 20px 0 20px;color:#64748b;font:600 13px/1 Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;">コメント</td></tr>
        <tr>
          <td style="padding:10px 20px 6px 20px;">
            <table role="presentation" width="100%">
              <tbody><tr>
                <td style="width:6px;background:{comment_bar_color};"></td>
                <td style="padding:8px 0 8px 12px;color:#334155;font:15px/1.8 Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;">{_comment_text}</td>
              </tr></tbody>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:2px 20px 0 20px;">
            <table role="presentation">
              <tbody><tr>
                <td align="center" style="width:40px;height:40px;background:#eef2f7;border-radius:50%;color:#64748b;font:700 18px Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;line-height:40px;vertical-align:middle;display:table-cell;">{_mono}</td>
                <td style="width:12px;"></td>
                <td style="color:#0f172a;font:600 15px/1.3 Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;">{_commenter_name}<br>
                  <span style="color:#64748b;font:12px/1.6 Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;">{_commenter_org}</span>
                </td>
              </tr></tbody>
            </table>
          </td>
        </tr>

        <tr>
          <td style="padding:12px 20px 18px 20px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
              <tbody><tr>
                <td style="background:#e8f0ff;border:1px solid #c7d2fe;border-radius:8px;">
                  <a href="{_link_url}" style="display:block;width:100%;text-align:center;color:#1d4ed8;text-decoration:none;font:700 15px/1 Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;padding:12px 18px;border-radius:8px;">
                    記事を読む
                  </a>
                </td>
              </tr></tbody>
            </table>
          </td>
        </tr>
      </tbody>
    </table>
    """
    return card_html


def render_email_full(
    title_text: str,
    badge_text: str,
    header_title: str,
    delivery_text: str,
    description_text: str,
    cards: List[str],
) -> str:
    """
    メール全体（ヘッダ＋カード群＋フッタ）を結合してHTMLを返す。
    """
    _title_text = escape_nl2br(title_text)
    _badge_text = escape_nl2br(badge_text)
    _header_title = escape_nl2br(header_title)
    _delivery_text = escape_nl2br(delivery_text)
    _description_text = escape_nl2br(description_text)

    # カード間のスペーサ
    spacer = '<div style="height:18px;line-height:18px;">&nbsp;</div>'

    body_cards_html = spacer.join(cards)

    html_full = f"""<meta charset="UTF-8">
<title>{_title_text}</title>

<!-- 100% wrapper -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0;padding:0;background:#f3f6fb;">
  <tbody><tr>
    <td align="center" style="padding:0;">

      <!-- ===== Header: full width background ===== -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#0b1b34;">
        <tbody><tr>
          <td align="center" style="padding:0;">
            <!-- inner fixed width -->
            <table role="presentation" width="900" cellpadding="0" cellspacing="0" border="0" style="max-width:900px;width:100%;">
              <tbody><tr>
                <td style="padding:20px 24px 12px 24px;">
                  <!-- row: badge + title -->
                  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tbody><tr>
                      <td>
                        <span style="display:inline-block;vertical-align:middle;background:#22315b;border:1px solid #2f3c66;color:#ffffff;font-weight:800;font-size:12px;letter-spacing:.04em;padding:7px 14px;border-radius:16px;font-family:Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;">{_badge_text}</span>
                        <span style="display:inline-block;vertical-align:middle;margin-left:12px;color:#ffffff;font-weight:800;font-size:22px;letter-spacing:.01em;font-family:Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;">{_header_title}</span>
                      </td>
                    </tr></tbody>
                  </table>
                  <!-- row: date -->
                  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tbody><tr>
                      <td style="padding-top:8px;color:#dbeafe;font-size:14px;font-family:Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;">{_delivery_text}</td>
                    </tr></tbody>
                  </table>
                  <!-- row: description -->
                  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tbody><tr>
                      <td style="padding-top:6px;color:#c7d2fe;font-size:13px;line-height:1.7;font-family:Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;">
                        {_description_text}
                      </td>
                    </tr></tbody>
                  </table>
                </td>
              </tr></tbody>
            </table>
          </td>
        </tr></tbody>
      </table>
      <!-- ===== /Header ===== -->

      <!-- ===== Body container ===== -->
      <table role="presentation" width="900" cellpadding="0" cellspacing="0" border="0" style="max-width:900px;width:100%;background:#f3f6fb;">
        <tbody><tr>
          <td style="padding:24px;">

            <!-- === Cards === -->
            {body_cards_html}

          </td>
        </tr></tbody>
      </table>
      <!-- ===== /Body ===== -->

      <!-- ===== Footer ===== -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#0b1b34;">
        <tbody><tr>
          <td align="center" style="padding:18px 12px;">
            <div style="color:#ffffff;font:12.5px/1.6 Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;">
              Copyright© 2016 Zeimu Kenkyukai, All rights reserved.
            </div>
            <div style="margin-top:8px;font-family:Arial,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;">
              <a href="https://www.zeiken.co.jp/privacy/" style="color:#ffffff;text-decoration:none;margin:0 10px;">個人情報の保護について</a>
              <a href="https://www.zeiken.co.jp/contact/request/" style="color:#ffffff;text-decoration:none;margin:0 10px;">お問い合わせ</a>
            </div>
          </td>
        </tr></tbody>
      </table>
      <!-- ===== /Footer ===== -->

    </td>
  </tr></tbody>
</table>
"""
    return html_full


# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="コメントクリップ HTMLメーカー", layout="wide")

st.title("コメントクリップ（HTMLメール）メーカー")
st.caption("週次の入力内容をフォームで設定 → HTMLを生成・プレビュー・ダウンロード")

with st.sidebar:
    st.header("入力方法")
    input_mode = st.radio(
        "カードの入力方法を選択",
        options=("フォームで入力", "CSVをアップロード"),
        index=0,
    )
    st.markdown("---")
    st.subheader("CSV仕様（任意）")
    st.markdown(
        """
**列名（ヘッダ必須）**  
- `issue`（例:`第3742号`）  
- `title`（記事タイトル）  
- `comment`（コメント本文）  
- `name`（氏名、例:`田中 太郎`）  
- `org`（所属）  
- `link`（ボタンのリンク。例:`#article1` またはURL）  
- `monogram`（任意。未指定なら自動）  
- `strip_color`（任意。例:`#c7d2fe`）
        """.strip()
    )

    # CSV雛形のダウンロード（任意）
    example_csv = (
        "issue,title,comment,name,org,link,monogram,strip_color\n"
        "第3742号,インボイス制度における返還インボイスの取扱い明確化,💬 コメント例をここに。複数行も可。,田中 太郎,田中税理士事務所,#article1,,#c7d2fe\n"
        "第3743号,デジタル経済における国際課税ルールの最新動向,💬 コメント例をここに。複数行も可。,佐藤 花子,ABC商事株式会社 経理部部長,#article2,,#a5b4fc\n"
    ).encode("utf-8")
    st.download_button(
        "CSV雛形をダウンロード",
        data=example_csv,
        file_name="comments_template.csv",
        mime="text/csv",
        use_container_width=True,
    )

# 基本設定
st.subheader("① 基本設定（ヘッダ）")
c1, c2, c3 = st.columns([1.2, 1.2, 1.0])

with c1:
    title_text = st.text_input(
        "メールの<title>（ブラウザ表示用）",
        value="コメントクリップ（メール配信用・全幅ヘッダー＆横長ボタン）",
    )
    badge_text = st.text_input("バッジ名", value="COMMENT CLIP")
with c2:
    header_title = st.text_input("ヘッダーの大見出し", value="週刊 税務通信")
    delivery_style = st.radio(
        "配信日の表記",
        options=("月日（例: 9月1日配信号）", "年月日（例: 2025年9月1日配信号）"),
        index=0,
    )
with c3:
    delivery_date = st.date_input("配信日", value=date.today())
    description_text = st.text_area(
        "説明文",
        value=(
            "多様な視点からのコメントが記事を読むきっかけとなり、普段触れない分野への関心を広げます。"
            "また、記事やコメントを記憶に残し、後々の読み返しを促すことで読み忘れを防ぐことを目的としています。"
            "※本メール内のコメントはコメンテーターの私見です"
        ),
        height=96,
    )

delivery_text = format_delivery_date(
    delivery_date, "MD" if delivery_style.startswith("月日") else "YMD"
)

# カード入力
st.subheader("② カード設定（記事＋コメント）")

cards_data: List[Dict[str, str]] = []

if input_mode == "CSVをアップロード":
    uploaded = st.file_uploader("CSVをアップロード", type=["csv"])
    if uploaded is not None:
        import pandas as pd

        try:
            df = pd.read_csv(uploaded)
            required_cols = {"issue", "title", "comment", "name", "org", "link"}
            if not required_cols.issubset(df.columns):
                st.error(f"CSVに必要な列が不足しています: {sorted(required_cols)}")
            else:
                for i, row in df.iterrows():
                    cards_data.append(
                        {
                            "issue": str(row.get("issue", "")).strip(),
                            "title": str(row.get("title", "")).strip(),
                            "comment": str(row.get("comment", "")).strip(),
                            "name": str(row.get("name", "")).strip(),
                            "org": str(row.get("org", "")).strip(),
                            "link": str(row.get("link", f"#article{i+1}")).strip(),
                            "monogram": str(row.get("monogram", "")).strip(),
                            "strip_color": str(row.get("strip_color", "")).strip(),
                        }
                    )
                st.success(f"{len(cards_data)} 件のカードを読み込みました。右側でプレビュー可能です。")
        except Exception as e:
            st.error(f"CSVの読み込みに失敗しました: {e}")

else:
    # フォームで入力
    comment_bar_color = st.color_picker(
        "コメント左バー（既定）は #2563eb", value="#2563eb", key="bar"
    )
    num_cards = st.number_input("カード数", min_value=1, max_value=20, value=3, step=1)

    for i in range(int(num_cards)):
        with st.expander(f"カード {i+1}", expanded=(i == 0)):
            col1, col2 = st.columns([1.0, 1.0])
            with col1:
                issue = st.text_input("号数（例: 第3742号）", key=f"issue_{i}", value=f"第{3742+i}号")
                title_ = st.text_input("記事タイトル", key=f"title_{i}", value="")
                strip_color = st.color_picker(
                    "カード上部ストリップ色", value=color_cycle(i), key=f"strip_{i}"
                )
            with col2:
                name = st.text_input("氏名（例: 田中 太郎）", key=f"name_{i}", value="")
                org = st.text_input("所属", key=f"org_{i}", value="")
                link = st.text_input(
                    "ボタンのリンク（#articleX または URL）",
                    key=f"link_{i}",
                    value=f"#article{i+1}",
                )
                mono = st.text_input(
                    "モノグラム（任意。空欄なら氏名から自動）", key=f"mono_{i}", value=""
                )

            comment = st.text_area(
                "コメント本文（複数行OK）", key=f"comment_{i}", value="💬 "
            )

            cards_data.append(
                {
                    "issue": issue,
                    "title": title_,
                    "comment": comment,
                    "name": name,
                    "org": org,
                    "link": link,
                    "monogram": mono,
                    "strip_color": strip_color,
                    "comment_bar_color": comment_bar_color,
                }
            )

# 生成・プレビュー
st.subheader("③ 生成・プレビュー・ダウンロード")

# カードHTMLを構築
cards_html_list: List[str] = []
for idx, c in enumerate(cards_data):
    cards_html_list.append(
        render_card(
            idx=idx,
            issue_label=c.get("issue", ""),
            article_title=c.get("title", ""),
            comment_text=c.get("comment", ""),
            commenter_name=c.get("name", ""),
            commenter_org=c.get("org", ""),
            link_url=c.get("link", f"#article{idx+1}"),
            strip_color=c.get("strip_color") or color_cycle(idx),
            monogram=c.get("monogram", ""),
            comment_bar_color=c.get("comment_bar_color", "#2563eb"),
        )
    )

# 全体HTML
full_html = render_email_full(
    title_text=title_text,
    badge_text=badge_text,
    header_title=header_title,
    delivery_text=delivery_text,
    description_text=description_text,
    cards=cards_html_list if cards_html_list else ["<!-- No cards -->"],
)

# 2カラム：左=ソース/ダウンロード、右=プレビュー
lc, rc = st.columns([1.0, 1.1])

with lc:
    st.markdown("**生成されたHTML（コピー用）**")
    st.text_area("HTMLソース", value=full_html, height=420, label_visibility="collapsed")

    fname = f"comment_clip_{delivery_date.strftime('%Y%m%d')}.html"
    st.download_button(
        "HTMLファイルをダウンロード",
        data=full_html.encode("utf-8"),
        file_name=fname,
        mime="text/html",
        use_container_width=True,
    )

with rc:
    st.markdown("**プレビュー（ブラウザ描画）**")
    # カード数に応じて高さを可変（ざっくり係数）
    preview_height = 520 + max(0, len(cards_html_list)) * 260
    try:
        st_html(full_html, height=min(max(preview_height, 600), 2400), scrolling=True)
    except Exception:
        # 万一、埋め込みに失敗した場合でもダウンロードは可能
        st.info("プレビュー表示に失敗しましたが、HTML自体はダウンロードできます。")


st.markdown("---")
with st.expander("使い方メモ", expanded=False):
    st.markdown(
        """
1. **基本設定**でバッジ名・ヘッダー・配信日・説明文を入力します。  
2. **カード設定**では、  
   - 入力方法に応じて、**フォーム**で1件ずつ入力するか、**CSV**をアップロードします。  
   - フォーム入力時は「カード数」を指定して各カードの内容を入力してください。  
   - モノグラムは未入力なら**氏名の先頭1文字**（スペース区切りなら**姓の先頭1文字**）を自動採用します。  
3. 右側でプレビューを確認し、**HTMLファイルをダウンロード**してください。  
4. 生成HTMLは**インラインスタイル**のためメール配信ツールにそのまま貼り付け可能です（各メールクライアントの描画差はご留意ください）。
        """.strip()
    )
