"""roster.html 의 스타일·공통 정의·배치 엔진을 오프라인 HTML 두 개에 넣는다."""
import pathlib

here = pathlib.Path(__file__).parent
s = (here.parent.parent / "roster.html").read_text(encoding="utf-8")
style = s[s.index("<style>"):s.index("</style>") + 8]
js = s.split("<script>")[1].split("</script>")[0]
common = js[js.index("const pad"):js.index("// ---------- 상태")]
engine = js[js.index("// ---------- 배치 엔진"):js.index("// ---------- 관리 화면")]
for name, out in (("survey", "불가시간_조사.html"), ("admin", "근무표_관리.html")):
    t = (here / f"{name}.tpl.html").read_text(encoding="utf-8")
    t = t.replace("/*STYLE*/", style).replace("/*COMMON*/", common).replace("/*ENGINE*/", engine)
    (here.parent / out).write_text(t, encoding="utf-8")
    print("wrote", out)
