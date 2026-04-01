#!/usr/bin/env node
// Departamentum Documentalis — emitter_wiz.js
// v1.0.0
// Reads a JSON AST from stdin or file arg, produces a .wiz document
// using the docx library and wizdoc style guide aesthetics.

const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel,
        AlignmentType, LevelFormat, BorderStyle, WidthType,
        ShadingType, Table, TableRow, TableCell, PageBreak } = require('docx');

// ── WizDoc Style Guide ──────────────────────────────────────
const C = {
    body:       'BDAB5D',
    h1:         'E8C96A',
    h2:         '7EC8C8',
    h3:         'A98FD4',
    h4:         'C87941',
    h5:         '8FAD8F',
    h6:         '8C7B5C',
    title:      'E8C96A',
    code_bg:    '1A1040',
    code_text:  '7EC8C8',
    tbl_hdr_fill: '2A1A4A',
    tbl_hdr_text: 'E8C96A',
    tbl_border:   '6B4E8A',
    tbl_hdr_bdr:  '8B6914',
    bg:         '050507',
    dim:        '8C7B5C',
    note:       '8FAD8F',
};

const FONTS = {
    title:  'Georgia',       // fallback; Ebon Sigil if available
    h1:     'Georgia',       // fallback; Varnyx Regular if available
    h2:     'Georgia',
    h3:     'Georgia',
    h4:     'Georgia',
    h5:     'Georgia',
    h6:     'Georgia',
    body:   'Georgia',       // fallback; VL Gothic if available
    code:   'Courier New',
};

const SIZES = {
    title: 56, h1: 36, h2: 28, h3: 24, h4: 22,
    h5: 20, h6: 20, body: 20, code: 18,
};

// ── Inline Span Rendering ───────────────────────────────────
function renderSpans(spans, defaultColor) {
    if (!spans || spans.length === 0) return [new TextRun({ text: '', color: defaultColor })];

    return spans.map(span => {
        const opts = {
            text: span.text || '',
            font: span.code ? FONTS.code : FONTS.body,
            size: span.code ? SIZES.code : SIZES.body,
            color: defaultColor,
        };
        if (span.bold) opts.bold = true;
        if (span.italic) opts.italics = true;
        if (span.code) {
            opts.color = C.code_text;
            opts.shading = { fill: C.code_bg, type: ShadingType.CLEAR };
        }
        if (span.color_token) {
            // Map token names to wizdoc colors where possible
            const tokenMap = {
                'c_gold': C.h1, 'c_gold_dim': C.dim,
                'c_teal': C.h2, 'c_crimson': C.h4,
                'c_text': C.body, 'c_white': C.h1,
            };
            opts.color = tokenMap[span.color_token] || defaultColor;
        }
        return new TextRun(opts);
    });
}

// ── Node → Paragraph(s) ────────────────────────────────────
function renderNode(node) {
    const tag = node.tag;
    const paragraphs = [];

    if (tag === 'break') {
        paragraphs.push(new Paragraph({ children: [new PageBreak()] }));
        return paragraphs;
    }

    // Headings
    const headingMap = {
        h1: { color: C.h1, size: SIZES.h1, bold: true, upper: true, spacing: { before: 400, after: 200 } },
        h2: { color: C.h2, size: SIZES.h2, bold: true, upper: false, spacing: { before: 300, after: 150 } },
        h3: { color: C.h3, size: SIZES.h3, bold: true, upper: false, spacing: { before: 200, after: 100 } },
        h4: { color: C.h4, size: SIZES.h4, bold: false, italic: true, spacing: { before: 200, after: 100 } },
        h5: { color: C.h5, size: SIZES.h5, bold: false, spacing: { before: 150, after: 80 } },
        h6: { color: C.h6, size: SIZES.h6, bold: false, spacing: { before: 150, after: 80 } },
    };

    if (headingMap[tag]) {
        const hcfg = headingMap[tag];
        let text = node.content || '';
        if (hcfg.upper) text = text.toUpperCase();
        const runs = (node.spans && node.spans.length > 0)
            ? renderSpans(node.spans, hcfg.color)
            : [new TextRun({
                text, font: FONTS[tag] || FONTS.body,
                size: hcfg.size, bold: hcfg.bold || false,
                italics: hcfg.italic || false, color: hcfg.color,
            })];
        paragraphs.push(new Paragraph({ spacing: hcfg.spacing, children: runs }));
        return paragraphs;
    }

    // Body
    if (tag === 'body') {
        const runs = (node.spans && node.spans.length > 0)
            ? renderSpans(node.spans, C.body)
            : [new TextRun({ text: node.content || '', font: FONTS.body, size: SIZES.body, color: C.body })];
        paragraphs.push(new Paragraph({ spacing: { after: 120 }, children: runs }));
        return paragraphs;
    }

    // Bullet
    if (tag === 'bullet') {
        const runs = (node.spans && node.spans.length > 0)
            ? renderSpans(node.spans, C.body)
            : [new TextRun({ text: node.content || '', font: FONTS.body, size: SIZES.body, color: C.body })];
        paragraphs.push(new Paragraph({
            numbering: { reference: 'bullets', level: 0 },
            spacing: { after: 60 },
            children: runs,
        }));
        return paragraphs;
    }

    // Note
    if (tag === 'note') {
        const runs = [new TextRun({
            text: node.content || '', font: FONTS.body,
            size: SIZES.body, color: C.note, italics: true,
        })];
        paragraphs.push(new Paragraph({ spacing: { after: 80 }, indent: { left: 360 }, children: runs }));
        return paragraphs;
    }

    // Quote
    if (tag === 'quote') {
        const runs = [new TextRun({
            text: node.content || '', font: FONTS.body,
            size: SIZES.body, color: C.dim, italics: true,
        })];
        paragraphs.push(new Paragraph({ spacing: { after: 80 }, indent: { left: 720 }, children: runs }));
        return paragraphs;
    }

    // Code block
    if (tag === 'code') {
        const codeLines = (node.content || '').split('\n');
        for (const cl of codeLines) {
            paragraphs.push(new Paragraph({
                shading: { fill: C.code_bg, type: ShadingType.CLEAR },
                spacing: { after: 0 },
                children: [new TextRun({ text: cl || ' ', font: FONTS.code, size: SIZES.code, color: C.code_text })],
            }));
        }
        // Small spacer after code block
        paragraphs.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
        return paragraphs;
    }

    // Table
    if (tag === 'table') {
        const rows = node.children || [];
        if (rows.length === 0) return paragraphs;

        const maxCols = Math.max(...rows.map(r => (r.children || []).length));
        const colWidth = Math.floor(9360 / maxCols);
        const border = { style: BorderStyle.SINGLE, size: 1, color: C.tbl_border };
        const hdrBorder = { style: BorderStyle.SINGLE, size: 1, color: C.tbl_hdr_bdr };
        const borders = { top: border, bottom: border, left: border, right: border };
        const hdrBorders = { top: hdrBorder, bottom: hdrBorder, left: hdrBorder, right: hdrBorder };

        const tableRows = rows.map(row => {
            const isHeader = row.tag === 'th';
            const cells = (row.children || []).map(cell => {
                const cellRuns = (cell.spans && cell.spans.length > 0)
                    ? renderSpans(cell.spans, isHeader ? C.tbl_hdr_text : C.body)
                    : [new TextRun({
                        text: cell.content || '',
                        font: FONTS.body, size: SIZES.body,
                        color: isHeader ? C.tbl_hdr_text : C.body,
                        bold: isHeader,
                    })];
                return new TableCell({
                    borders: isHeader ? hdrBorders : borders,
                    width: { size: colWidth, type: WidthType.DXA },
                    shading: isHeader
                        ? { fill: C.tbl_hdr_fill, type: ShadingType.CLEAR }
                        : { fill: C.bg, type: ShadingType.CLEAR },
                    margins: { top: 80, bottom: 80, left: 120, right: 120 },
                    children: [new Paragraph({ children: cellRuns })],
                });
            });
            // Pad with empty cells if needed
            while (cells.length < maxCols) {
                cells.push(new TableCell({
                    borders, width: { size: colWidth, type: WidthType.DXA },
                    children: [new Paragraph({ children: [] })],
                }));
            }
            return new TableRow({ children: cells, cantSplit: true });
        });

        const columnWidths = Array(maxCols).fill(colWidth);
        paragraphs.push(new Table({
            width: { size: 9360, type: WidthType.DXA },
            columnWidths,
            rows: tableRows,
        }));
        paragraphs.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
        return paragraphs;
    }

    // Fallback — render as body
    paragraphs.push(new Paragraph({
        spacing: { after: 100 },
        children: [new TextRun({ text: node.content || '', font: FONTS.body, size: SIZES.body, color: C.body })],
    }));
    return paragraphs;
}

// ── Main Build ──────────────────────────────────────────────
async function build(astJson, outputPath) {
    const ast = JSON.parse(astJson);
    const header = ast.header || {};
    const nodes = ast.nodes || [];

    const numbering = {
        config: [{
            reference: 'bullets',
            levels: [{ level: 0, format: LevelFormat.BULLET, text: '\u2022',
                alignment: AlignmentType.LEFT,
                style: { paragraph: { indent: { left: 720, hanging: 360 } },
                         run: { color: C.body } } }],
        }],
    };

    const children = [];

    // Document title
    if (header.title) {
        children.push(new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 400 },
            children: [new TextRun({
                text: header.title, font: FONTS.title,
                size: SIZES.title, bold: true, color: C.title,
            })],
        }));
    }

    // Render all nodes
    for (const node of nodes) {
        const paras = renderNode(node);
        children.push(...paras);
    }

    const doc = new Document({
        numbering,
        background: { color: C.bg },
        sections: [{
            properties: {
                page: {
                    size: { width: 12240, height: 15840 },
                    margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
                },
            },
            children,
        }],
    });

    const buffer = await Packer.toBuffer(doc);
    fs.writeFileSync(outputPath, buffer);
}

// ── CLI Entry ───────────────────────────────────────────────
const args = process.argv.slice(2);
if (args.length < 2) {
    console.error('Usage: node emitter_wiz.js <ast.json> <output.wiz>');
    process.exit(1);
}

const astJson = fs.readFileSync(args[0], 'utf-8');
build(astJson, args[1]).then(() => {
    // silent success
}).catch(e => {
    console.error('emitter_wiz.js error:', e.message);
    process.exit(1);
});
