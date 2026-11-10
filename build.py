"""Build colorful progress dashboards (self-contained HTML) from .xer, .mpp and MS Project .xml files.
Usage: python build.py [input_dir] [output_dir]   (defaults: input, docs)
.mpp files are converted to MSPDI XML with MPXJ (needs Java). .xer / .xml need no Java.
"""
import sys, json, html, pathlib, tempfile

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "input")
out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "docs")
out.mkdir(parents=True, exist_ok=True)
tpl = pathlib.Path(__file__).parent.joinpath("template", "dashboard.html").read_text(encoding="utf-8")

def mpp_to_xml(path):
    import jpype, jpype.imports, mpxj  # noqa: F401
    if not jpype.isJVMStarted():
        jpype.startJVM()
    try:
        from org.mpxj.reader import UniversalProjectReader
        from org.mpxj.mspdi import MSPDIWriter
    except ImportError:  # MPXJ < 13
        from net.sf.mpxj.reader import UniversalProjectReader
        from net.sf.mpxj.mspdi import MSPDIWriter
    project = UniversalProjectReader().read(str(path))
    if project is None:
        raise RuntimeError("MPXJ could not read " + path.name)
    with tempfile.TemporaryDirectory() as d:
        x = pathlib.Path(d) / "p.xml"
        MSPDIWriter().write(project, str(x))
        return x.read_text(encoding="utf-8")

built = []
for f in sorted(src.iterdir()):
    ext = f.suffix.lower()
    if ext not in (".xer", ".mpp", ".xml"):
        continue
    try:
        if ext == ".mpp":
            text, is_xml = mpp_to_xml(f), True
        elif ext == ".xml":
            text, is_xml = f.read_text(encoding="utf-8", errors="replace"), True
        else:
            text, is_xml = f.read_bytes().decode("cp1252", errors="replace"), False
    except Exception as e:
        print("FAILED", f.name, e); continue
    payload = json.dumps({"name": f.name, "xml": is_xml, "text": text}).replace("</", "<\\/")
    page = tpl.replace("<!--PRELOAD-->", "<script>window.PRELOAD=" + payload + ";</script>", 1)
    name = f.stem.replace(" ", "_") + ".html"
    (out / name).write_text(page, encoding="utf-8")
    built.append((f.name, name)); print("built", name)

links = "".join(f'<li><a href="{html.escape(n)}">{html.escape(s)}</a></li>' for s, n in built)
(out / "index.html").write_text(
    '<!DOCTYPE html><meta charset="utf-8"><title>Dashboards</title><body style="font:16px system-ui;background:#0b1020;color:#e8ecff;padding:30px">'
    f"<h2>Progress dashboards</h2><ul>{links or '<li>No input files</li>'}</ul>"
    '<p>You can also open any dashboard and upload another .xer / .xml file.</p>', encoding="utf-8")
