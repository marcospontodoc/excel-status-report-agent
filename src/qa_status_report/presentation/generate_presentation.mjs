import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const modulePath = process.env.QA_ARTIFACT_TOOL_MODULE;
if (!modulePath) throw new Error('QA_ARTIFACT_TOOL_MODULE não foi configurado.');
const { Presentation, PresentationFile } = await import(pathToFileURL(modulePath).href);

const inputChunks = [];
for await (const chunk of process.stdin) inputChunks.push(chunk);
const payload = JSON.parse(Buffer.concat(inputChunks).toString('utf8'));
const outputPath = path.resolve(process.argv[2]);
const previewDir = path.resolve(process.argv[3]);
await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const C = {
  navy: '#17324D', ink: '#172B3A', muted: '#5B6B78', paper: '#FFFFFF',
  line: '#D9E1E8', pale: '#F3F6F8', red: '#C94747', gray: '#8A9299',
  amber: '#D99523', blue: '#3383A7', green: '#32835B',
};
const statusColors = [C.red, C.gray, C.amber, C.blue, C.green];
const p = Presentation.create({ slideSize: { width: 1280, height: 720 } });

function addText(slide, text, x, y, w, h, opts = {}) {
  const shape = slide.shapes.add({
    geometry: 'textbox',
    name: opts.name || 'text',
    position: { left: x, top: y, width: w, height: h },
    fill: 'none',
    line: { style: 'solid', fill: 'none', width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: opts.size ?? 22,
    typeface: 'Arial',
    color: opts.color ?? C.ink,
    bold: opts.bold ?? false,
    alignment: opts.align ?? 'left',
    verticalAlignment: opts.valign ?? 'middle',
    wrap: true,
    autoFit: 'shrinkText',
    insets: { left: 0, right: 0, top: 0, bottom: 0 },
  };
  return shape;
}

function addBaseSlide(title, number) {
  const slide = p.slides.add();
  slide.background.fill = C.paper;
  addText(slide, title, 64, 38, 1148, 56, { size: 34, bold: true, color: C.navy, name: `title-${number}` });
  const divider = slide.shapes.add({
    geometry: 'rect', name: `divider-${number}`,
    position: { left: 64, top: 105, width: 1152, height: 2 },
    fill: C.line, line: { style: 'solid', fill: C.line, width: 0 },
  });
  return slide;
}

function refList(origins) {
  return (origins || []).map(o => `${o.sheet}!${o.coordinate} (${o.column})`);
}

function formatDate(iso) {
  return new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC' }).format(new Date(`${iso}T00:00:00Z`));
}

function setNotes(slide, lines) {
  slide.speakerNotes.text = lines.filter(Boolean).join('\n');
}

function makeTable(slide, values, widths, bounds, opts = {}) {
  const colCount = values[0].length;
  const bodyRows = Math.max(0, values.length - 1);
  const widthsSum = widths.reduce((a, b) => a + b, 0);
  const maxRows = opts.maxRows ?? 24;
  if (bodyRows > maxRows) throw new Error(`A tabela do slide ${opts.slide} tem ${bodyRows} registros; o layout de quatro slides comporta até ${maxRows} sem reduzir a leitura. Não foi gerado um relatório parcial.`);

  const usableHeight = bounds.height;
  const headerHeight = 40;
  const heights = values.slice(1).map(row => {
    const lines = row.reduce((max, value, index) => {
      const charsPerLine = Math.max(8, Math.floor(widths[index] / 8));
      const renderedLines = String(value ?? '').split('\n').reduce((sum, line) => sum + Math.max(1, Math.ceil(line.length / charsPerLine)), 0);
      return Math.max(max, renderedLines);
    }, 1);
    return Math.max(24, 18 * lines + 6);
  });
  const totalHeight = headerHeight + heights.reduce((a, b) => a + b, 0);
  if (totalHeight > usableHeight) throw new Error(`O conteúdo da tabela do slide ${opts.slide} não cabe com leitura adequada. Reduza ou divida os registros no arquivo de entrada; nenhum registro foi omitido.`);

  const table = slide.tables.add({
    rows: values.length,
    columns: colCount,
    left: bounds.left,
    top: bounds.top,
    width: bounds.width,
    height: totalHeight,
    columnWidths: widths.map(width => (width / widthsSum) * bounds.width),
    values,
  });
  table.styleOptions = { headerRow: true, bandedRows: true };
  table.borders.assign({ style: 'solid', fill: C.line, width: 1 });
  for (let col = 0; col < colCount; col += 1) {
    table.getCell(0, col).fill = C.navy;
  }
  table.cells.block({ row: 0, column: 0, rowCount: 1, columnCount: colCount }).assign({
    textStyle: { fontSize: 16, color: C.paper, bold: true, typeface: 'Arial' },
    margins: { left: 8, right: 8, top: 4, bottom: 4 },
  });
  if (bodyRows) {
    table.cells.block({ row: 1, column: 0, rowCount: bodyRows, columnCount: colCount }).assign({
      textStyle: { fontSize: opts.fontSize ?? 15, color: C.ink, typeface: 'Arial' },
      margins: { left: 8, right: 8, top: 4, bottom: 4 },
    });
  }
  table.rows[0].height = headerHeight;
  heights.forEach((height, index) => { table.rows[index + 1].height = height; });
  return table;
}

// Slide 1 — project and reporting period.
{
  const slide = p.slides.add();
  slide.background.fill = C.paper;
  slide.shapes.add({
    geometry: 'rect', name: 'cover-rule',
    position: { left: 64, top: 96, width: 10, height: 500 },
    fill: C.navy, line: { style: 'solid', fill: C.navy, width: 0 },
  });
  addText(slide, 'STATUS REPORT DE QA', 104, 120, 1000, 36, { size: 18, bold: true, color: C.muted });
  addText(slide, payload.project.name, 104, 192, 1050, 190, { size: 46, bold: true, color: C.navy, name: 'project-name' });
  addText(slide, 'Período de execução', 104, 424, 700, 34, { size: 18, color: C.muted });
  addText(slide, `${formatDate(payload.project.period_start)} – ${formatDate(payload.project.period_end)}`, 104, 466, 760, 52, { size: 28, color: C.ink });
  setNotes(slide, [
    `Arquivo de origem: ${payload.source_workbook}`,
    'Fontes do projeto e período:',
    ...refList(payload.project.origins),
  ]);
}

// Slide 2 — five-category pie and planned total.
{
  const slide = addBaseSlide('Cenários de teste', 2);
  addText(slide, 'CENÁRIOS PLANEJADOS', 76, 174, 350, 32, { size: 18, bold: true, color: C.muted });
  addText(slide, String(payload.planned_scenarios), 76, 214, 350, 105, { size: 76, bold: true, color: C.navy });
  addText(slide, 'Total cadastrado na aba Cenários', 76, 320, 330, 55, { size: 20, color: C.muted });
  const counts = payload.status_distribution.map(row => row.count);
  if (counts.some(count => count > 0)) {
    const chart = slide.charts.add('pie', {
      position: { left: 430, top: 136, width: 770, height: 510 },
      categories: payload.status_distribution.map(row => row.status),
      series: [{ name: 'Contagem', values: counts, points: statusColors.map((fill, idx) => ({ idx, fill })) }],
      hasLegend: true,
      legend: { position: 'right', overlay: false },
      pieOptions: { firstSliceAngle: 270 },
      dataLabels: { showCategoryName: true, showValue: true, showPercent: false, separator: ': ', position: 'outEnd', textStyle: { fontSize: 14, fill: C.ink } },
      chartFill: 'none', chartLine: { style: 'solid', fill: 'none', width: 0 },
      plotAreaFill: 'none', plotAreaLine: { style: 'solid', fill: 'none', width: 0 },
    });
    for (const style of [chart.legend?.textStyle, chart.dataLabels?.textStyle]) {
      if (style) style.typeface = 'Arial';
    }
  } else {
    addText(slide, 'Nenhum cenário cadastrado', 500, 300, 600, 60, { size: 28, color: C.muted, align: 'center' });
  }
  const formulaNotes = payload.notes.filter(note => note.code === 'formula_cache_used' || note.code === 'formula_without_cache');
  if (formulaNotes.length) addText(slide, 'Fórmulas não foram recalculadas; valores em cache podem estar desatualizados e valores sem cache ficam indisponíveis.', 76, 615, 1120, 34, { size: 13, color: C.muted });
  setNotes(slide, [
    `Arquivo de origem: ${payload.source_workbook}`,
    'Distribuição: contagem dos cenários em cada categoria; status vazio foi tratado como Em Andamento.',
    'Total planejado: número de registros válidos de cenários; não é uma categoria da pizza.',
    ...payload.status_distribution.flatMap(item => [`${item.status}: ${item.count}`, ...refList(item.origins || [])]),
    ...formulaNotes.map(note => `${note.message}${note.origin ? ` em ${note.origin.sheet}!${note.origin.coordinate}` : ''}`),
  ]);
}

// Slide 3 — one row per functionality, with scenario observations grouped verbatim.
{
  const slide = addBaseSlide('Progresso por funcionalidade', 3);
  const rows = [['Funcionalidade', 'Status', 'Progresso', 'Bugs', 'Observações dos cenários']];
  for (const item of payload.functionalities) {
    rows.push([
      item.name,
      item.status ?? 'Sem cenários',
      item.progress_percent === null ? 'Indisponível' : `${item.progress_percent}%`,
      String(item.bug_count),
      item.observation_summary ?? (item.observation_unavailable ? 'Observação indisponível: fórmula sem valor em cache.' : 'Não foram registradas observações.'),
    ]);
  }
  if (rows.length === 1) rows.push(['Nenhuma funcionalidade cadastrada', '—', 'Indisponível', '0', '—']);
  const widths = [245, 125, 120, 80, 582];
  makeTable(slide, rows, widths, { left: 64, top: 132, width: 1152, height: 536 }, { slide: 3, fontSize: 15, maxRows: 20 });
  const refs = payload.functionalities.flatMap(item => [
    `Funcionalidade ${item.id} — ${item.name}:`,
    ...refList(item.status_origins),
    ...refList(item.progress_origins),
    ...refList(item.bug_origins),
    ...refList(item.observation_origins),
  ]);
  setNotes(slide, [
    `Arquivo de origem: ${payload.source_workbook}`,
    'Progresso = (Aprovado + Falha) / cenários não ignorados. Status funcional segue a precedência documentada no projeto.',
    'Observações são agrupadas por funcionalidade e preservam o texto original, rotulado pelo ID do cenário. Não há reescrita por IA.',
    ...refs,
  ]);
}

// Slide 4 — every registered bug, linked by explicit IDs in the source.
{
  const slide = addBaseSlide('Bugs registrados', 4);
  const rows = [['ID', 'Descrição', 'Status', 'Severidade', 'Responsável', 'Abertura']];
  for (const bug of payload.bugs) rows.push([bug.id, bug.description, bug.status, bug.severity, bug.responsible, formatDate(bug.opened_at)]);
  if (!payload.bugs.length) rows.push(['—', 'Nenhum bug cadastrado', '—', '—', '—', '—']);
  const widths = [112, 460, 148, 142, 172, 118];
  makeTable(slide, rows, widths, { left: 64, top: 132, width: 1152, height: 536 }, { slide: 4, fontSize: 14, maxRows: 20 });
  setNotes(slide, [
    `Arquivo de origem: ${payload.source_workbook}`,
    `Fonte: aba Bugs. Registros de bugs: ${payload.bugs.length}.`,
    ...payload.bugs.flatMap(bug => [`${bug.id}:`, ...refList(bug.origins)]),
  ]);
}

for (const [index, slide] of p.slides.items.entries()) {
  const image = await p.export({ slide, format: 'png', scale: 1 });
  await fs.writeFile(path.join(previewDir, `slide-${index + 1}.png`), new Uint8Array(await image.arrayBuffer()));
}
const pptx = await PresentationFile.exportPptx(p);
await pptx.save(outputPath);
await fs.rm(`${outputPath}.inspect.ndjson`, { force: true });
console.log(JSON.stringify({ output: outputPath, slides: p.slides.items.length }));

