"use client";

import { useState, useRef, useCallback } from "react";
import "./globals.css";
import { buildPreviewHtml } from "../components/preview";

const API = process.env.NEXT_PUBLIC_API || "http://localhost:8000";

export default function Page() {
  const [imgUrl, setImgUrl] = useState(null);
  const [natural, setNatural] = useState({ w: 0, h: 0 });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState("code");
  const [over, setOver] = useState(false);
  const fileRef = useRef(null);
  const stageImg = useRef(null);

  const handleFile = useCallback(async (file) => {
    if (!file || !file.type.startsWith("image/")) return;
    setError(null); setResult(null);
    setImgUrl(URL.createObjectURL(file));
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${API}/api/generate`, { method: "POST", body: fd });
      if (!res.ok) {
        const j = await res.json().catch(() => ({}));
        throw new Error(j.detail || `Request failed (${res.status})`);
      }
      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const onDrop = (e) => { e.preventDefault(); setOver(false); handleFile(e.dataTransfer.files?.[0]); };
  const scale = stageImg.current && natural.w ? stageImg.current.clientWidth / natural.w : 1;

  return (
    <div className="shell">
      <div className="masthead">
        <div className="logo">Pixel<b>Draft</b></div>
        <div className="tagline">screenshot &rarr; editable React</div>
      </div>
      <div className="rule" />

      <div className="grid">
        <div className="panel">
          <div className="panel-head">
            <span>input &mdash; detected layout</span>
            {result && <span>{result.elements.length} elements</span>}
          </div>
          <div className="panel-body">
            {!imgUrl ? (
              <div className={"drop" + (over ? " over" : "")}
                onClick={() => fileRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setOver(true); }}
                onDragLeave={() => setOver(false)}
                onDrop={onDrop}>
                <h3>Drop a UI screenshot</h3>
                <p>or click to browse &mdash; PNG or JPG of a simple interface</p>
                <div className="hint">login forms, dashboards, cards, settings pages work best</div>
              </div>
            ) : (
              <div className="stage">
                <img ref={stageImg} src={imgUrl} alt="uploaded UI"
                  onLoad={(e) => setNatural({ w: e.target.naturalWidth, h: e.target.naturalHeight })} />
                {result?.elements.map((el, i) => (
                  <div key={i} className="box" style={{
                    left: el.box[0] * scale, top: el.box[1] * scale,
                    width: (el.box[2] - el.box[0]) * scale,
                    height: (el.box[3] - el.box[1]) * scale }}>
                    <span className="tag">{el.type}</span>
                  </div>
                ))}
              </div>
            )}
            <div className="status">
              {loading && <span><span className="spinner" /> detecting &amp; generating&hellip;</span>}
              {result && <span>page <b>{result.size[0]}&times;{result.size[1]}</b></span>}
              {imgUrl && !loading && (
                <span className="btn ghost" style={{ padding: "4px 10px" }}
                  onClick={() => { setImgUrl(null); setResult(null); setError(null); }}>reset</span>
              )}
            </div>
            {error && <div className="err" style={{ marginTop: 10 }}>error: {error}</div>}
            <input ref={fileRef} type="file" accept="image/*" hidden
              onChange={(e) => handleFile(e.target.files?.[0])} />
          </div>
        </div>

        <div className="panel">
          <div className="panel-head">
            <div className="tabs">
              <span className="tab active">React</span>
            </div>
            {result && (
              <span className="btn ghost" style={{ padding: "4px 10px" }}
                onClick={() => navigator.clipboard.writeText(result.code)}>copy</span>
            )}
          </div>
          <div className="panel-body">
            {!result ? (
              <div className="empty">generated React + Tailwind will appear here</div>
            ) : (
              <pre className="code">{result.code}</pre>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
