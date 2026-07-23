"""묶기용 신호(카테고리 + 주체 타입·이름) 파일 생성 — data/signals/articles90.json.

주체는 **정답 라벨을 보지 않고** 90건의 제목+짧은요약만 읽어 손으로 뽑았다
(운영에선 1단계 분류 LLM이 category와 함께 낼 값 — plick-ai README §8.1, KAN-273/275).
주체 = (타입: player·manager·club 등) + (이름: 영어 canonical). 파티션 키로 쓴다.

같은 사건을 다룬 기사는 같은 (category, subject_name)을 갖도록 맞췄다. 여러 인물이
나오면 기사의 핵심 1명을 고른다(불완전한 실제 추출을 흉내). 재현: 이 스크립트를 돌리면
같은 파일이 나온다(결정적).
"""

import json

from plick_embedding.settings import PROJECT_ROOT

# id -> (category, subject_type, subject_name)
SIGNALS: dict[str, tuple[str, str, str]] = {
    "6882": ("TRANSFER", "player", "quenda"),
    "6884": ("TRANSFER", "player", "guimaraes"),
    "6886": ("TRANSFER", "player", "greenwood"),
    "6887": ("TRANSFER", "player", "palhinha"),
    "6890": ("TRANSFER", "player", "deri"),
    "6891": ("OTHER", "manager", "maresca"),
    "6894": ("TRANSFER", "player", "santos"),
    "6895": ("TRANSFER", "player", "guimaraes"),
    "6896": ("TRANSFER", "player", "tchouameni"),
    "6898": ("TRANSFER", "player", "ederson"),
    "6899": ("TRANSFER", "player", "guimaraes"),
    "6913": ("TRANSFER", "player", "santos"),
    "6922": ("OTHER", "player", "guehi"),
    "6925": ("TRANSFER", "player", "guimaraes"),
    "6927": ("OTHER", "manager", "amorim"),
    "6928": ("TRANSFER", "player", "santos"),
    "6943": ("TRANSFER", "player", "guimaraes"),
    "6945": ("OTHER", "player", "merino"),
    "6949": ("OTHER", "manager", "alonso"),
    "6970": ("TRANSFER", "player", "meslier"),
    "6971": ("OTHER", "player", "haaland"),
    "6977": ("OTHER", "player", "stones"),
    "6992": ("TRANSFER", "player", "dalot"),
    "6993": ("OTHER", "manager", "alonso"),
    "6998": ("TRANSFER", "player", "santos"),
    "6999": ("OTHER", "player", "mbappe"),
    "7016": ("TRANSFER", "player", "romero"),
    "7018": ("OTHER", "manager", "alonso"),
    "7024": ("TRANSFER", "player", "dalot"),
    "7026": ("MATCH", "player", "haaland"),
    "7037": ("MATCH", "manager", "tuchel"),
    "7038": ("FITNESS", "player", "guehi"),
    "7047": ("TRANSFER", "player", "charles"),
    "7055": ("OTHER", "player", "maguire"),
    "7057": ("TRANSFER", "player", "charles"),
    "7060": ("OTHER", "player", "vandijk"),
    "7064": ("TRANSFER", "player", "santos"),
    "7069": ("TRANSFER", "player", "santos"),
    "7077": ("MATCH", "player", "merino"),
    "7092": ("TRANSFER", "club", "manutd_midfielders"),
    "7093": ("TRANSFER", "player", "tzolis"),
    "7096": ("TRANSFER", "player", "ederson"),
    "7105": ("FITNESS", "player", "courtois"),
    "7107": ("MATCH", "player", "merino"),
    "7108": ("MATCH", "player", "merino"),
    "7110": ("MATCH", "player", "guehi"),
    "7111": ("OTHER", "player", "guehi"),
    "7121": ("TRANSFER", "player", "nypan"),
    "7123": ("TRANSFER", "player", "garnacho"),
    "7124": ("TRANSFER", "player", "salah"),
    "7126": ("TRANSFER", "player", "nypan"),
    "7131": ("TRANSFER", "player", "monga"),
    "7155": ("MATCH", "player", "konsa"),
    "7166": ("OTHER", "manager", "iraola"),
    "7169": ("OTHER", "player", "haaland"),
    "7180": ("TRANSFER", "player", "deri"),
    "7197": ("OTHER", "player", "mainoo"),
    "7213": ("OTHER", "player", "haaland"),
    "7216": ("MATCH", "player", "haaland"),
    "7223": ("OTHER", "player", "haaland"),
    "7225": ("MATCH", "player", "spence"),
    "7227": ("MATCH", "player", "haaland"),
    "7229": ("FITNESS", "player", "stones"),
    "7230": ("MATCH", "player", "spence"),
    "7231": ("MATCH", "player", "haaland"),
    "7232": ("MATCH", "player", "selderup"),
    "7239": ("MATCH", "player", "macallister"),
    "7246": ("OTHER", "player", "haaland"),
    "7264": ("OTHER", "player", "haaland"),
    "7317": ("TRANSFER", "player", "greenwood"),
    "7328": ("TRANSFER", "player", "trossard"),
    "7342": ("TRANSFER", "player", "konate"),
    "7343": ("TRANSFER", "player", "tielemans"),
    "7344": ("TRANSFER", "player", "tielemans"),
    "7345": ("TRANSFER", "player", "tielemans"),
    "7346": ("TRANSFER", "player", "ederson"),
    "7347": ("OTHER", "manager", "iraola"),
    "7349": ("TRANSFER", "player", "tielemans"),
    "7350": ("TRANSFER", "player", "tielemans"),
    "7351": ("TRANSFER", "player", "tielemans"),
    "7352": ("TRANSFER", "player", "tielemans"),
    "7353": ("TRANSFER", "player", "tielemans"),
    "7354": ("TRANSFER", "player", "tielemans"),
    "7357": ("OTHER", "manager", "iraola"),
    "7358": ("TRANSFER", "club", "manutd_midfielders"),
    "7359": ("OTHER", "manager", "iraola"),
    "7361": ("TRANSFER", "player", "chavarria"),
    "7362": ("TRANSFER", "player", "tielemans"),
    "7364": ("TRANSFER", "player", "ederson"),
    "7365": ("OTHER", "manager", "iraola"),
}


def main() -> None:
    articles_path = PROJECT_ROOT / "data" / "articles.json"
    out_path = PROJECT_ROOT / "data" / "signals" / "articles90.json"

    ids = [str(r["id"]) for r in json.loads(articles_path.read_text(encoding="utf-8"))]
    missing = [i for i in ids if i not in SIGNALS]
    extra = [i for i in SIGNALS if i not in ids]
    if missing or extra:
        raise SystemExit(f"신호 불일치 — 누락 {missing} · 잉여 {extra}")

    out = {
        i: {"category": c, "subject_type": t, "subject_name": n} for i, (c, t, n) in SIGNALS.items()
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"신호 {len(out)}건 저장: {out_path}")


if __name__ == "__main__":
    main()
