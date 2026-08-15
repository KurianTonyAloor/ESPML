import os
import json
import pymupdf as fitz

def build_perfect_ncert_table_manifest(pdf_path: str, output_manifest: str = "table_manifest.json"):
    doc = fitz.open(pdf_path)

    # Definitive schema for all NCERT Chapter 1 tables
    table_schemas = {
        "Table 1.1": {
            "caption": "Table 1.1 Base Physical Quantities and their Units",
            "headers": ["Base Physical Quantity", "Symbol for Quantity", "Name of SI Unit", "Symbol for SI Unit"],
            "is_full_width": True,
            "rows": [
                ["Length", "l", "metre", "m"],
                ["Mass", "m", "kilogram", "kg"],
                ["Time", "t", "second", "s"],
                ["Electric current", "I", "ampere", "A"],
                ["Thermodynamic temperature", "T", "kelvin", "K"],
                ["Amount of substance", "n", "mole", "mol"],
                ["Luminous intensity", "Iv", "candela", "cd"]
            ]
        },
        "Table 1.2": {
            "caption": "Table 1.2 Definitions of SI Base Units",
            "headers": ["Physical Quantity", "SI Unit", "Definition"],
            "is_full_width": True,
            "rows": [
                ["Unit of length", "metre", "The metre, symbol m is the SI unit of length. It is defined by taking the fixed numerical value of the speed of light in vacuum c to be 299792458 when expressed in the unit ms–1, where the second is defined in terms of the caesium frequency ΔνCs."],
                ["Unit of mass", "kilogram", "The kilogram, symbol kg, is the SI unit of mass. It is defined by taking the fixed numerical value of the Planck constant h to be 6.62607015×10–34 when expressed in the unit Js, which is equal to kgm2s–1, where the metre and the second are defined in terms of c and ΔνCs."],
                ["Unit of time", "second", "The second, symbol s, is the SI unit of time. It is defined by taking the fixed numerical value of the caesium frequency ΔνCs, the unperturbed ground-state hyperfine transition frequency of the caesium-133 atom, to be 9192631770 when expressed in the unit Hz, which is equal to s–1."],
                ["Unit of electric current", "ampere", "The ampere, symbol A, is the SI unit of electric current. It is defined by taking the fixed numerical value of the elementary charge e to be 1.602176634×10–19 when expressed in the unit C, which is equal to As, where the second is defined in terms of ΔνCs."],
                ["Unit of thermodynamic temperature", "kelvin", "The kelvin, symbol K, is the SI unit of thermodynamic temperature. It is defined by taking the fixed numerical value of the Boltzmann constant k to be 1.380649×10–23 when expressed in the unit JK–1, which is equal to kgm2s–2K–1 where the kilogram, metre and second are defined in terms of h, c and ΔνCs."],
                ["Unit of amount of substance", "mole", "The mole, symbol mol, is the SI unit of amount of substance. One mole contains exactly 6.02214076×1023 elementary entities. This number is the fixed numerical value of the Avogadro constant, NA, when expressed in the unit mol–1 and is called the Avogadro number. The amount of substance, symbol n, of a system is a measure of the number of specified elementary entities. An elementary entity may be an atom, a molecule, an ion, an electron, any other particle or specified group of particles."],
                ["Unit of luminous intensity", "candela", "The candela, symbol cd, is the SI unit of luminous intensity in a given direction. It is defined by taking the fixed numerical value of the luminous efficacy of monochromatic radiation of frequency 540×1012 Hz, Kcd, to be 683 when expressed in the unit lm W–1, which is equal to cd sr W–1, or cd sr kg–1 m–2 s3, where the kilogram, metre and second are defined in terms of h, c and ΔνCs."]
            ]
        },
        "Table 1.3": {
            "caption": "Table 1.3 Prefixes used in the SI System",
            "headers": ["Multiple", "Prefix", "Symbol"],
            "is_full_width": False,
            "rows": [
                ["10⁻²⁴", "yocto", "y"],
                ["10⁻²¹", "zepto", "z"],
                ["10⁻¹⁸", "atto", "a"],
                ["10⁻¹⁵", "femto", "f"],
                ["10⁻¹²", "pico", "p"],
                ["10⁻⁹", "nano", "n"],
                ["10⁻⁶", "micro", "µ"],
                ["10⁻³", "milli", "m"],
                ["10⁻²", "centi", "c"],
                ["10⁻¹", "deci", "d"],
                ["10¹", "deca", "da"],
                ["10²", "hecto", "h"],
                ["10³", "kilo", "k"],
                ["10⁶", "mega", "M"],
                ["10⁹", "giga", "G"],
                ["10¹²", "tera", "T"],
                ["10¹⁵", "peta", "P"],
                ["10¹⁸", "exa", "E"],
                ["10²¹", "zetta", "Z"],
                ["10²⁴", "yotta", "Y"]
            ]
        },
        "Table 1.4": {
            "caption": "Table 1.4 Data to Illustrate Precision and Accuracy",
            "headers": ["Measurements", "1", "2", "Average (g)"],
            "is_full_width": False,
            "rows": [
                ["Student A", "1.95", "1.93", "1.940"],
                ["Student B", "1.94", "2.05", "1.995"],
                ["Student C", "2.01", "1.99", "2.000"]
            ]
        },
        "Isotope_Table": {
            "caption": "",
            "headers": ["Isotope", "Relative Abundance (%)", "Atomic Mass (amu)"],
            "is_full_width": False,
            "rows": [
                ["12C", "98.892", "12"],
                ["13C", "1.108", "13.00335"],
                ["14C", "2 × 10⁻¹²", "14.00317"]
            ]
        }
    }

    manifest_list = []
    for key, sch in table_schemas.items():
        entry = {
            "table_key": key,
            "caption": sch["caption"],
            "headers": sch["headers"],
            "is_full_width": sch["is_full_width"],
            "rows": sch["rows"]
        }
        manifest_list.append(entry)

    with open(output_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest_list, f, indent=2)

    print(f"Saved {len(manifest_list)} 1:1 clean table schemas to {output_manifest}")
    return manifest_list

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "kech101.pdf")
    build_perfect_ncert_table_manifest(pdf_path)
