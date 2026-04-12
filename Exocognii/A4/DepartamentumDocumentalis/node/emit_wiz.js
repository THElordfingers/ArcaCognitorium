"use strict";
// Departamentum Documentalis · emit_wiz.js · v1.1
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, HeadingLevel } = require("docx");

const payloadPath = process.argv[2];
if (!payloadPath) { console.error("Usage: node emit_wiz.js <payload.json>"); process.exit(1); }

const { doc: blocks, output: outPath } = JSON.parse(fs.readFileSync(payloadPath, "utf8"));

const children = (blocks || []).map(b => {
    if (b.type === "heading")
        return new Paragraph({ heading: HeadingLevel.HEADING_2,
            children: [new TextRun({ text: b.text, bold: true, font: "Georgia" })] });
    if (b.type === "field")
        return new Paragraph({ children: [
            new TextRun({ text: (b.label || "") + ": ", bold: true, font: "Georgia" }),
            new TextRun({ text: b.value || "", font: "Courier Prime" }) ] });
    return new Paragraph({ children: [new TextRun({ text: b.text || "", font: "Georgia" })] });
});

const doc = new Document({
    styles: { default: { document: { run: { font: "Georgia", size: 24 } } } },
    sections: [{ properties: { page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
    }}, children }]
});

Packer.toBuffer(doc)
    .then(buf => { fs.writeFileSync(outPath, buf); console.log("OK: " + outPath); })
    .catch(e  => { console.error(e.message); process.exit(1); });
