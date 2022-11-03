from enum import Enum

FACULTY_ABBREVIATIONS = {'Theologische Fakultät': 'Theol',
                         'Rechtswissenschaftliche Fakultät': 'RWF',
                         'Medizinische Fakultät': 'MF',
                         'Philosophische Fakultät': 'Phil',
                         'Agrar- und Ernährungswissenschaftliche Fakultät': 'AEF',
                         'Mathematisch-Naturwissenschaftliche Fakultät': 'MNF',
                         'Wirtschafts- und Sozialwissenschaftliche Fakultät': 'WiSo',
                         'Technische Fakultät': 'TF',
                         'Erziehungswissenschaftliche Fakultät': 'Erziehung'}

FACULTY_COLORS = {
    'Theologische Fakultät': '#562381',
    'Rechtswissenschaftliche Fakultät': '#e43117',
    'Medizinische Fakultät': '#99c221',
    'Philosophische Fakultät': '#6aacda',
    'Agrar- und Ernährungswissenschaftliche Fakultät': '#39842e',
    'Mathematisch-Naturwissenschaftliche Fakultät': '#f29400',
    'Wirtschafts- und Sozialwissenschaftliche Fakultät': '#005459',
    'Technische Fakultät': '#003d86',
    'Erziehungswissenschaftliche Fakultät': '#f2c200'
}


class Faculty(Enum):
    """
    Valid faculties of the Uni-Kiel.
    """
    AGRAR = "Agrar- und Ernährungswissenschaftliche Fakultät"
    MATHE = "Mathematisch-Naturwissenschaftliche Fakultät"
    MEDIZI = "Medizinische Fakultät"
    THEOL = "Theologische Fakultät"
    PHILOS = "Philosophische Fakultät"
    RECHTS = "Rechtswissenschaftliche Fakultät"
    TECHN = 'Technische Fakultät'
    WIRTSC = "Wirtschafts- und Sozialwissenschaftliche Fakultät"
    ERZIEH = 'Erziehungswissenschaftliche Fakultät'

    def __str__(self) -> str:
        return f'{self.value}'
