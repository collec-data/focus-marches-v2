import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { formatBoolean, formatDate, structureName } from './HelpersService';

import type { ContratConcessionDto, MarcheAllegeDto, StructureAggMarchesDto } from '@/client';
import { utils, writeFileXLSX } from 'xlsx';

/** Used for excel exports */
function mapElementToColumnName(element: Array<string>, columns: Array<string>): any {
    const result = {};
    for (let i = 0; i < element.length; i++) {
        result[columns[i]] = element[i];
    }
    return result;
}

const structure_columns = ['Nom', 'Montant', 'Contrats'];

function formatStructureList(structures: StructureAggMarchesDto[]): Array<any> {
    return structures.map((structure) => [structureName(structure.structure), parseFloat(structure.montant), structure.nb_contrats]);
}

const marche_columns = ['ID', 'CPV', 'Objet', 'Acheteur', 'Fournisseur', 'Sous\n-trait', 'Cons \nEnv', 'Cons \nSoc', 'Date', 'Durée \n(mois)', 'Montant'];
const marche_columns_style = {
    columnStyles: {
        0: { cellWidth: 25 },
        1: { cellWidth: 20 },
        2: { cellWidth: 70 },
        3: { cellWidth: 30 },
        4: { cellWidth: 30 },
        5: { cellWidth: 13 },
        6: { cellWidth: 13 },
        7: { cellWidth: 13 },
        8: { cellWidth: 22 },
        9: { cellWidth: 15 },
        10: { cellWidth: 25 }
    }
};

function formatMarchesList(marches: MarcheAllegeDto[]): Array<any> {
    return marches.map((marche) => [
        marche.id,
        marche.cpv.code + ' \n' + marche.cpv.libelle,
        marche.objet,
        structureName(marche.acheteur),
        marche.titulaires.map((t) => structureName(t)).join(' \n'),
        formatBoolean(marche.sous_traitance_declaree),
        formatBoolean(marche.considerations_environnementales?.length > 0),
        formatBoolean(marche.considerations_sociales?.length > 0),
        formatDate(marche.date_notification),
        marche.duree_mois,
        parseFloat(marche.montant)
    ]);
}

const concession_columns = ['ID', 'Objet', 'Concessionnaires', 'Date \nsignature', 'Date \nexec', 'Valeur \nglobale'];
function formatConcessionsList(concessions: ContratConcessionDto[]): Array<any> {
    return concessions.map((concession) => [
        concession.id,
        concession.objet,
        concession.concessionnaires.map((c) => structureName(c)).join(' \n'),
        formatDate(concession.date_signature),
        formatDate(concession.date_debut_execution),
        concession.valeur_globale
    ]);
}

function exportCSV(rows: Array<Array<any>>, columns: Array<string>, file_name: string) {
    const csvContent =
        'data:text/csv;charset=utf-8,' +
        columns
            .map((e) => e.replace('\n', ''))
            .map((c) => '"' + c + '"')
            .join(',') +
        '\n' +
        rows.map((row) => row.map((cell) => '"' + cell.toString().replace('\n', '').replace('"', '""') + '"').join(',')).join('\n');
    const encodedUri = encodeURI(csvContent);
    const a = document.createElement('a');
    a.href = encodedUri;
    a.download = file_name + '.csv';
    a.click();
}

function exportPdf(rows: Array<Array<any>>, columns: Array<any>, title: string, file_name: string, columns_style: any = { styles: { minCellWidth: 20 } }) {
    const doc = new jsPDF({ orientation: 'landscape' });
    doc.text(title, 10, 5);
    autoTable(doc, { head: [columns], body: rows, margin: 0, startY: 10, ...columns_style });
    doc.save(file_name + '.pdf');
}

export function exportStructuresPdf(structures: StructureAggMarchesDto[], title: string, file_name: string) {
    exportPdf(formatStructureList(structures), structure_columns, title, file_name);
}

export function exportStructuresCSV(structures: StructureAggMarchesDto[], file_name: string) {
    exportCSV(formatStructureList(structures), structure_columns, file_name);
}

export function exportStructuresExcel(structures: StructureAggMarchesDto[], file_name: string) {
    writeFileXLSX({ Sheets: { data: utils.json_to_sheet(formatStructureList(structures).map((structure) => mapElementToColumnName(structure, structure_columns))) }, SheetNames: ['data'] }, file_name + '.xlsx');
}

export function exportMarchesPdf(marches: MarcheAllegeDto[], title: string, file_name: string = 'marches') {
    exportPdf(formatMarchesList(marches), marche_columns, title, file_name, marche_columns_style);
}

export function exportMarchesCSV(marches: MarcheAllegeDto[], file_name: string = 'marches') {
    exportCSV(formatMarchesList(marches), marche_columns, file_name);
}

export function exportMarchesExcel(marches: MarcheAllegeDto[], file_name: string = 'marches') {
    writeFileXLSX({ Sheets: { data: utils.json_to_sheet(formatMarchesList(marches).map((marche) => mapElementToColumnName(marche, marche_columns))) }, SheetNames: ['data'] }, file_name + '.xlsx');
}

export function exportConcessionsPdf(concessions: ContratConcessionDto[], title: string, file_name: string = 'concessions') {
    exportPdf(formatConcessionsList(concessions), concession_columns, title, file_name);
}

export function exportConcessionsCSV(concessions: ContratConcessionDto[], file_name: string = 'concessions') {
    exportCSV(formatConcessionsList(concessions), concession_columns, file_name);
}

export function exportConcessionsExcel(concessions: ContratConcessionDto[], file_name: string = 'concessions') {
    writeFileXLSX({ Sheets: { data: utils.json_to_sheet(formatConcessionsList(concessions).map((concession) => mapElementToColumnName(concession, concession_columns))) }, SheetNames: ['data'] }, file_name + '.xlsx');
}
