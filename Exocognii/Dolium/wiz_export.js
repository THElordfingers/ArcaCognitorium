/**
 * wiz_export.js — Dolium v2
 * Generates a .wiz file (styled .docx) from a JSON idea manifest.
 * Invoked by ExportEngine._to_wiz() via subprocess.
 *
 * Usage: node wiz_export.js <manifest.json> <output.wiz>
 *
 * Requires: npm install docx
 */

"use strict";

const fs   = require("fs");
const path = require("path");

// ── Arg validation ────────────────────────────────────────────────────────────

const [, , manifestPath, outputPath] = process.argv;

if (!manifestPath || !outputPath) {
    console.error("Usage: node wiz_export.js <manifest.json> <output.wiz>");
    process.exit(1);
}

if (!fs.existsSync(manifestPath)) {
    console.error(`Manifest not found: ${manifestPath}`);
    process.exit(1);
}

// ── Load docx ─────────────────────────────────────────────────────────────────

let docx;
try {
    docx = require("docx");
} catch (e) {
    console.error("docx package not installed. Run: npm install docx");
    process.exit(1);
}

const {
    Document,
    Paragraph,
    TextRun,
    HeadingLevel,
    AlignmentType,
    BorderStyle,
    Packer,
} = docx;

// ── Load manifest ─────────────────────────────────────────────────────────────

let idea;
try {
    idea = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
} catch (e) {
    console.error(`Failed to parse manifest: ${e.message}`);
    process.exit(1);
}

// ── Modus Arcanus colours (hex, no #) ────────────────────────────────────────

const C_GOLD     = "D4AF37";
const C_TEXT     = "C8B88A";
const C_DIM      = "6A5F4A";
const C_CRIMSON  = "8B1A1A";
const C_BG       = "050507";

// ── Document builders ─────────────────────────────────────────────────────────

function makeTitle(text) {
    return new Paragraph({
        children: [
            new TextRun({
                text,
                bold:  true,
                size:  36,
                color: C_GOLD,
                font:  "Georgia",
            }),
        ],
        spacing: { after: 200 },
    });
}

function makeSubtitle(text) {
    return new Paragraph({
        children: [
            new TextRun({
                text,
                size:  20,
                color: C_DIM,
                italics: true,
                font:  "Georgia",
            }),
        ],
        spacing: { after: 400 },
    });
}

function makeSectionHeading(text) {
    return new Paragraph({
        children: [
            new TextRun({
                text: text.toUpperCase(),
                bold:          true,
                size:          20,
                color:         C_GOLD,
                font:          "Georgia",
                characterSpacing: 40,
            }),
        ],
        spacing: { before: 300, after: 100 },
        border: {
            bottom: {
                color: C_DIM,
                space: 1,
                value: BorderStyle.SINGLE,
                size:  4,
            },
        },
    });
}

function makeBody(text) {
    if (!text || !text.trim()) return null;
    return new Paragraph({
        children: [
            new TextRun({
                text: text.trim(),
                size: 22,
                color: C_TEXT,
                font: "Georgia",
            }),
        ],
        spacing: { after: 200 },
    });
}

function makeSeparator() {
    return new Paragraph({
        children: [new TextRun({ text: "· · ·", color: C_DIM, size: 18, font: "Georgia" })],
        alignment: AlignmentType.CENTER,
        spacing: { before: 200, after: 200 },
    });
}

// ── Ordered sections ──────────────────────────────────────────────────────────

const SECTIONS = [
    ["Body",          "body"],
    ["Motivation",    "motivation"],
    ["Elaboration",   "elaboration"],
    ["Obstacles",     "obstacles"],
    ["First Step",    "first_step"],
    ["Refined Form",  "refined_form"],
    ["Open Problems", "open_problems"],
    ["Next Actions",  "next_actions"],
    ["Declaration",   "declaration"],
    ["Summary",       "summary"],
];

// ── Assemble document ─────────────────────────────────────────────────────────

const children = [];

// Title block
children.push(makeTitle(idea.title || "(untitled)"));

const chamberNames = {
    1: "I · The Fomentary",
    2: "II · The Cultivation House",
    3: "III · The Vestibule",
    4: "IV · The Codex",
};
const chamberLabel = chamberNames[idea.chamber] || `Chamber ${idea.chamber}`;
const dateLabel    = new Date().toISOString().slice(0, 10);
children.push(makeSubtitle(`${chamberLabel}  ·  ${dateLabel}`));
children.push(makeSeparator());

// Content sections
for (const [label, key] of SECTIONS) {
    const text = idea[key];
    if (text && text.trim()) {
        children.push(makeSectionHeading(label));
        children.push(makeBody(text));
    }
}

// Tags
if (idea.tags && idea.tags.length > 0) {
    children.push(makeSectionHeading("Tags"));
    children.push(makeBody(idea.tags.map(t => `#${t}`).join("  ")));
}

// ── Build & write ─────────────────────────────────────────────────────────────

const doc = new Document({
    sections: [{
        properties: {
            page: {
                margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
            },
        },
        children,
    }],
    background: { color: C_BG },
});

Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync(outputPath, buffer);
    console.log(`Written: ${outputPath}`);
    process.exit(0);
}).catch(err => {
    console.error(`Pack failed: ${err.message}`);
    process.exit(1);
});
