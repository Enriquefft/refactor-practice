"""
Programa para calcular el ganador de entre los candidatos.

Este programa lee un archivo csv con los datos de las votaciones y calcula el
ganador de entre los candidatos. El archivo csv tiene el siguiente formato:
    region,provincia,distrito,dni,candidato,esvalido

Un candidato es ganador si tiene más del 50% de votos válidos.
Si no hay un ganador, se calculan los candidatos que pasan a segunda vuelta.
Si hay empate, se retorna el candidato que apareció primero en el archivo.

"""

from csv import DictReader
from typing import Final, TypedDict, Any, Literal, Optional
from pathlib import Path
from collections import defaultdict

from dataclasses import dataclass

import logging as log

# Typedefs


# DictReader fieldnames
class CsvEntry(TypedDict, total=False):
    """Tipo de datos de una entrada de votos.csv."""

    region: str
    provincia: str
    distrito: str
    dni: int
    candidato: str
    esvalido: bool


# Constants
CSV_PATH: Final[Path] = Path('votos.csv')

DATATEST: Final[list[CsvEntry]] = [{
    'region': 'Áncash',
    'provincia': 'Asunción',
    'distrito': 'Acochaca',
    'dni': 40810062,
    'candidato': 'Eddie Hinesley',
    'esvalido': False
}, {
    'region': 'Áncash',
    'provincia': 'Asunción',
    'distrito': 'Acochaca',
    'dni': 57533597,
    'candidato': 'Eddie Hinesley',
    'esvalido': True
}, {
    'region': 'Áncash',
    'provincia': 'Asunción',
    'distrito': 'Acochaca',
    'dni': 86777322,
    'candidato': 'Aundrea Grace',
    'esvalido': True
}, {
    'region': 'Áncash',
    'provincia': 'Asunción',
    'distrito': 'Acochaca',
    'dni': 23017965,
    'candidato': 'Aundrea Grace',
    'esvalido': True
}]

KeyNames = Literal['region', 'provincia', 'distrito', 'dni', 'candidato',
                   'esvalido']


def toLiteral(s: str) -> KeyNames:
    """Small hack to allow string literals as DictReader fieldnames."""
    if s == 'region':
        return 'region'
    elif s == 'provincia':
        return 'provincia'
    elif s == 'distrito':
        return 'distrito'
    elif s == 'dni':
        return 'dni'
    elif s == 'candidato':
        return 'candidato'
    elif s == 'esvalido':
        return 'esvalido'
    raise ValueError(f'Key {s} is not a valid key name')


def parseCsvEntry(input_dict: dict[str | Any, str | Any],
                  line: int) -> CsvEntry:
    """Parsea un diccionario a CsvEntry."""
    result: CsvEntry = {}
    for key, k_type in CsvEntry.__annotations__.items():
        if key not in input_dict:
            log.info(input_dict)
            log.error(f'Key {key} not found in input_dict at line {line}')
        if not isinstance(input_dict[key], k_type):
            try:
                input_dict[key] = k_type(input_dict[key])
            except ValueError:
                log.error(
                    f'Key {key} couldn\'t be casted to type {type(input_dict[key])}, expected {k_type}. Error at line {line}'
                )
        result[toLiteral(key)] = input_dict[key]
    return result


class CalculaGanador:
    """Calcula el ganador de votos válidos."""

    def __init__(self, csv_path: Optional[Path] = None):
        """Inicializa el objeto."""
        self.csv_path = csv_path
        self.vote_list: list[CsvEntry] = []
        self.valid_votes: int = 0

        if self.csv_path is None:
            log.info('Using test data')
            self.vote_list = DATATEST
            for vote in self.vote_list:
                if vote['esvalido']:
                    self.valid_votes += 1
        else:
            log.info(f'Using csv data from {self.csv_path}')
            self.leerdatos()

    def leerdatos(self) -> None:
        """Lee los datos del archivo votos.csv."""
        with open(CSV_PATH, 'r') as csvfile:
            next(csvfile)
            datareader = DictReader(csvfile)
            for line_count, fila in enumerate(datareader):
                entry: CsvEntry = parseCsvEntry(fila, line_count)
                self.vote_list.append(entry)
                if entry['esvalido']:
                    self.valid_votes += 1

    def run(self) -> tuple[str, Optional[str]]:
        """Calcula el ganador contando los votos válidos."""
        votosxcandidato: dict[str, int] = defaultdict(int)
        for vote in self.vote_list:
            if vote['esvalido']:
                votosxcandidato[vote['candidato']] += 1

        for candidato in votosxcandidato:
            print(
                f'candidato: {candidato} votos validos: {votosxcandidato[candidato]}'
            )
        first, second = self.getTop2(votosxcandidato)

        if first.votes > self.valid_votes / 2:
            return first.name, None
        return first.name, second.name

    @dataclass
    class Candidato:
        """Representa un candidato."""

        name: str
        votes: int

    def getTop2(
            self, votosxcandidato: dict[str,
                                        int]) -> tuple[Candidato, Candidato]:
        """Calcula los 2 candidatos con mayor cantidad de votos."""
        top: CalculaGanador.Candidato = CalculaGanador.Candidato('', 0)
        second: CalculaGanador.Candidato = CalculaGanador.Candidato('', 0)

        for name, vote_count in votosxcandidato.items():
            if vote_count > top.votes:
                second = top
                top = CalculaGanador.Candidato(name, vote_count)
            elif vote_count > second.votes:
                second = CalculaGanador.Candidato(name, vote_count)
        return top, second


# c = CalculaGanador()
c = CalculaGanador(CSV_PATH)
primer, segundo = c.run()
