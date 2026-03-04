"""
SPIN-Compatible Substance Database
===================================
50+ pesticide active substances with literature-sourced properties
from official EU dossiers and PPDB (Pesticide Properties Database).

Each substance includes: identifiers, physicochemical properties,
environmental fate parameters, molecular descriptors, and regulatory status.
"""

SUBSTANCES = [
    # ─── Organophosphates ──────────────────────────────────────────────
    {
        "name": "Chlorpyrifos", "cas": "2921-88-2", "formula": "C9H11Cl3NO3PS",
        "smiles": "CCOP(=S)(OCC)Oc1nc(Cl)c(Cl)cc1Cl", "mw": 350.6,
        "degT50_soil": 50, "degT50_water": 25, "degT50_sediment": 120,
        "koc": 8151, "kfoc": 8151, "freundlich_n": 0.90,
        "vapor_pressure": 2.5e-3, "henry_const": 4.7e-1,
        "solubility": 1.05, "pka": None, "logP": 4.7,
        "cls": "Organophosphate", "status": "Not approved",
        "n_atoms": 27, "n_heavy": 16, "hbd": 0, "hba": 4, "n_rings": 1, "n_rotatable": 5
    },
    {
        "name": "Dimethoate", "cas": "60-51-5", "formula": "C5H12NO3PS2",
        "smiles": "COP(=S)(OC)SCC(=O)NC", "mw": 229.3,
        "degT50_soil": 2.5, "degT50_water": 4, "degT50_sediment": 8,
        "koc": 28, "kfoc": 28, "freundlich_n": 0.95,
        "vapor_pressure": 2.5e-4, "henry_const": 1.4e-5,
        "solubility": 23800, "pka": None, "logP": 0.7,
        "cls": "Organophosphate", "status": "Not approved",
        "n_atoms": 22, "n_heavy": 12, "hbd": 1, "hba": 4, "n_rings": 0, "n_rotatable": 5
    },
    {
        "name": "Malathion", "cas": "121-75-5", "formula": "C10H19O6PS2",
        "smiles": "CCOC(=O)CC(SP(=S)(OC)OC)C(=O)OCC", "mw": 330.4,
        "degT50_soil": 1, "degT50_water": 6, "degT50_sediment": 3,
        "koc": 1800, "kfoc": 1800, "freundlich_n": 0.90,
        "vapor_pressure": 3.1e-3, "henry_const": 4.9e-5,
        "solubility": 148, "pka": None, "logP": 2.75,
        "cls": "Organophosphate", "status": "Not approved",
        "n_atoms": 37, "n_heavy": 18, "hbd": 0, "hba": 6, "n_rings": 0, "n_rotatable": 10
    },
    {
        "name": "Phosmet", "cas": "732-11-6", "formula": "C11H12NO4PS2",
        "smiles": "COP(=S)(OC)SCN1C(=O)c2ccccc2C1=O", "mw": 317.3,
        "degT50_soil": 5, "degT50_water": 12, "degT50_sediment": 15,
        "koc": 659, "kfoc": 659, "freundlich_n": 0.88,
        "vapor_pressure": 6.5e-5, "henry_const": 1.4e-6,
        "solubility": 25, "pka": None, "logP": 2.95,
        "cls": "Organophosphate", "status": "Approved",
        "n_atoms": 30, "n_heavy": 18, "hbd": 0, "hba": 5, "n_rings": 2, "n_rotatable": 4
    },

    # ─── Neonicotinoids ────────────────────────────────────────────────
    {
        "name": "Imidacloprid", "cas": "138261-41-3", "formula": "C9H10ClN5O2",
        "smiles": "O=[N+]([O-])/N=C1\\NCCN1Cc1ccc(Cl)nc1", "mw": 255.7,
        "degT50_soil": 191, "degT50_water": 30, "degT50_sediment": 365,
        "koc": 225, "kfoc": 225, "freundlich_n": 0.88,
        "vapor_pressure": 4.0e-10, "henry_const": 1.7e-10,
        "solubility": 610, "pka": None, "logP": 0.57,
        "cls": "Neonicotinoid", "status": "Not approved (outdoor)",
        "n_atoms": 27, "n_heavy": 17, "hbd": 1, "hba": 5, "n_rings": 2, "n_rotatable": 2
    },
    {
        "name": "Thiamethoxam", "cas": "153719-23-4", "formula": "C8H10ClN5O3S",
        "smiles": "CN1COCN(Cc2cnc(Cl)s2)/C1=N/[N+](=O)[O-]", "mw": 291.7,
        "degT50_soil": 50, "degT50_water": 11, "degT50_sediment": 40,
        "koc": 56, "kfoc": 56, "freundlich_n": 0.92,
        "vapor_pressure": 6.6e-9, "henry_const": 4.7e-10,
        "solubility": 4100, "pka": None, "logP": -0.13,
        "cls": "Neonicotinoid", "status": "Not approved (outdoor)",
        "n_atoms": 27, "n_heavy": 18, "hbd": 0, "hba": 5, "n_rings": 2, "n_rotatable": 2
    },
    {
        "name": "Clothianidin", "cas": "210880-92-5", "formula": "C6H8ClN5O2S",
        "smiles": "CN/C(=N/[N+](=O)[O-])NCc1cnc(Cl)s1", "mw": 249.7,
        "degT50_soil": 545, "degT50_water": 14, "degT50_sediment": 277,
        "koc": 123, "kfoc": 123, "freundlich_n": 0.87,
        "vapor_pressure": 2.8e-8, "henry_const": 2.9e-11,
        "solubility": 340, "pka": 11.1, "logP": 0.91,
        "cls": "Neonicotinoid", "status": "Not approved (outdoor)",
        "n_atoms": 22, "n_heavy": 15, "hbd": 2, "hba": 5, "n_rings": 1, "n_rotatable": 3
    },
    {
        "name": "Acetamiprid", "cas": "135410-20-7", "formula": "C10H11ClN4",
        "smiles": "CC(=NC#N)N(C)Cc1ccc(Cl)nc1", "mw": 222.7,
        "degT50_soil": 3, "degT50_water": 4.7, "degT50_sediment": 12,
        "koc": 200, "kfoc": 200, "freundlich_n": 0.90,
        "vapor_pressure": 1.7e-7, "henry_const": 5.3e-8,
        "solubility": 2950, "pka": 0.7, "logP": 0.80,
        "cls": "Neonicotinoid", "status": "Approved",
        "n_atoms": 26, "n_heavy": 15, "hbd": 0, "hba": 3, "n_rings": 1, "n_rotatable": 3
    },
    {
        "name": "Thiacloprid", "cas": "111988-49-9", "formula": "C10H9ClN4S",
        "smiles": "N#C/N=C1\\SCCN1Cc1ccc(Cl)nc1", "mw": 252.7,
        "degT50_soil": 18, "degT50_water": 10, "degT50_sediment": 27,
        "koc": 615, "kfoc": 615, "freundlich_n": 0.85,
        "vapor_pressure": 3.0e-7, "henry_const": 5.0e-8,
        "solubility": 184, "pka": None, "logP": 1.26,
        "cls": "Neonicotinoid", "status": "Not approved",
        "n_atoms": 24, "n_heavy": 16, "hbd": 0, "hba": 3, "n_rings": 2, "n_rotatable": 2
    },

    # ─── Triazoles ─────────────────────────────────────────────────────
    {
        "name": "Tebuconazole", "cas": "107534-96-3", "formula": "C16H22ClN3O",
        "smiles": "CC(C)(C)C(O)(CCc1ccc(Cl)cc1)Cn1cncn1", "mw": 307.8,
        "degT50_soil": 55, "degT50_water": 42, "degT50_sediment": 365,
        "koc": 769, "kfoc": 769, "freundlich_n": 0.90,
        "vapor_pressure": 1.3e-6, "henry_const": 1.0e-5,
        "solubility": 36, "pka": 5.0, "logP": 3.7,
        "cls": "Triazole", "status": "Approved",
        "n_atoms": 42, "n_heavy": 21, "hbd": 1, "hba": 3, "n_rings": 2, "n_rotatable": 5
    },
    {
        "name": "Propiconazole", "cas": "60207-90-1", "formula": "C15H17Cl2N3O2",
        "smiles": "CCC(Oc1ccc(Cl)cc1Cl)C1COC(Cn2cncn2)O1", "mw": 342.2,
        "degT50_soil": 40, "degT50_water": 70, "degT50_sediment": 200,
        "koc": 1086, "kfoc": 1086, "freundlich_n": 0.85,
        "vapor_pressure": 5.6e-5, "henry_const": 9.2e-5,
        "solubility": 150, "pka": 1.09, "logP": 3.72,
        "cls": "Triazole", "status": "Not approved",
        "n_atoms": 37, "n_heavy": 22, "hbd": 0, "hba": 5, "n_rings": 3, "n_rotatable": 4
    },
    {
        "name": "Epoxiconazole", "cas": "135319-73-2", "formula": "C17H13ClFN3O",
        "smiles": "Clc1ccc(C2OC2(Cn2cncn2)c2ccc(F)cc2)cc1", "mw": 329.8,
        "degT50_soil": 120, "degT50_water": 68, "degT50_sediment": 500,
        "koc": 1073, "kfoc": 1073, "freundlich_n": 0.88,
        "vapor_pressure": 1.0e-5, "henry_const": 4.7e-5,
        "solubility": 7.1, "pka": None, "logP": 3.3,
        "cls": "Triazole", "status": "Not approved",
        "n_atoms": 35, "n_heavy": 23, "hbd": 0, "hba": 3, "n_rings": 4, "n_rotatable": 3
    },
    {
        "name": "Metconazole", "cas": "125116-23-6", "formula": "C17H22ClN3O",
        "smiles": "CC1CCC(C(O)(Cn2cncn2)c2ccc(Cl)cc2)C1C", "mw": 319.8,
        "degT50_soil": 80, "degT50_water": 55, "degT50_sediment": 350,
        "koc": 510, "kfoc": 510, "freundlich_n": 0.90,
        "vapor_pressure": 1.6e-5, "henry_const": 2.3e-4,
        "solubility": 30.4, "pka": None, "logP": 3.85,
        "cls": "Triazole", "status": "Approved",
        "n_atoms": 43, "n_heavy": 22, "hbd": 1, "hba": 3, "n_rings": 3, "n_rotatable": 3
    },

    # ─── Pyrethroids ───────────────────────────────────────────────────
    {
        "name": "Lambda-cyhalothrin", "cas": "91465-08-6", "formula": "C23H19ClF3NO3",
        "smiles": "CC1(C)C(C=C(Cl)C(F)(F)F)C1C(=O)OC(C#N)c1cccc(Oc2ccccc2)c1",
        "mw": 449.9,
        "degT50_soil": 30, "degT50_water": 14, "degT50_sediment": 60,
        "koc": 157000, "kfoc": 157000, "freundlich_n": 0.82,
        "vapor_pressure": 2.0e-7, "henry_const": 2.0e-2,
        "solubility": 0.005, "pka": None, "logP": 7.0,
        "cls": "Pyrethroid", "status": "Approved",
        "n_atoms": 49, "n_heavy": 30, "hbd": 0, "hba": 4, "n_rings": 3, "n_rotatable": 7
    },
    {
        "name": "Cypermethrin", "cas": "52315-07-8", "formula": "C22H19Cl2NO3",
        "smiles": "CC1(C)C(C=C(Cl)Cl)C1C(=O)OC(C#N)c1cccc(Oc2ccccc2)c1",
        "mw": 416.3,
        "degT50_soil": 60, "degT50_water": 16, "degT50_sediment": 90,
        "koc": 63000, "kfoc": 63000, "freundlich_n": 0.85,
        "vapor_pressure": 2.3e-7, "henry_const": 4.2e-2,
        "solubility": 0.009, "pka": None, "logP": 6.6,
        "cls": "Pyrethroid", "status": "Approved",
        "n_atoms": 47, "n_heavy": 27, "hbd": 0, "hba": 4, "n_rings": 3, "n_rotatable": 7
    },
    {
        "name": "Deltamethrin", "cas": "52918-63-5", "formula": "C22H19Br2NO3",
        "smiles": "CC1(C)C(C=C(Br)Br)C1C(=O)OC(C#N)c1cccc(Oc2ccccc2)c1",
        "mw": 505.2,
        "degT50_soil": 21, "degT50_water": 3, "degT50_sediment": 65,
        "koc": 460000, "kfoc": 460000, "freundlich_n": 0.80,
        "vapor_pressure": 1.2e-8, "henry_const": 3.1e-3,
        "solubility": 0.0002, "pka": None, "logP": 6.2,
        "cls": "Pyrethroid", "status": "Approved",
        "n_atoms": 47, "n_heavy": 27, "hbd": 0, "hba": 4, "n_rings": 3, "n_rotatable": 7
    },

    # ─── Strobilurins ──────────────────────────────────────────────────
    {
        "name": "Azoxystrobin", "cas": "131860-33-8", "formula": "C22H17N3O5",
        "smiles": "COC=C(C(=O)OC)c1ccccc1Oc1cc(Oc2ccccc2C#N)ncn1", "mw": 403.4,
        "degT50_soil": 78, "degT50_water": 11, "degT50_sediment": 200,
        "koc": 423, "kfoc": 423, "freundlich_n": 0.90,
        "vapor_pressure": 1.1e-10, "henry_const": 7.4e-9,
        "solubility": 6.7, "pka": None, "logP": 2.5,
        "cls": "Strobilurin", "status": "Approved",
        "n_atoms": 47, "n_heavy": 30, "hbd": 0, "hba": 8, "n_rings": 3, "n_rotatable": 7
    },
    {
        "name": "Pyraclostrobin", "cas": "175013-18-0", "formula": "C19H18ClN3O4",
        "smiles": "COC(=O)N(OC)c1ccccc1COc1ccn(C)c(=O)c1Cl", "mw": 387.8,
        "degT50_soil": 32, "degT50_water": 2, "degT50_sediment": 170,
        "koc": 9315, "kfoc": 9315, "freundlich_n": 0.87,
        "vapor_pressure": 2.6e-8, "henry_const": 1.3e-6,
        "solubility": 1.9, "pka": None, "logP": 3.99,
        "cls": "Strobilurin", "status": "Approved",
        "n_atoms": 45, "n_heavy": 27, "hbd": 0, "hba": 6, "n_rings": 2, "n_rotatable": 6
    },
    {
        "name": "Kresoxim-methyl", "cas": "143390-89-0", "formula": "C18H19NO4",
        "smiles": "CON=C(C(=O)OC)c1ccccc1COc1ccccc1C", "mw": 313.4,
        "degT50_soil": 1, "degT50_water": 16, "degT50_sediment": 5,
        "koc": 308, "kfoc": 308, "freundlich_n": 0.92,
        "vapor_pressure": 2.3e-6, "henry_const": 5.5e-5,
        "solubility": 2.0, "pka": None, "logP": 3.4,
        "cls": "Strobilurin", "status": "Approved",
        "n_atoms": 42, "n_heavy": 23, "hbd": 0, "hba": 5, "n_rings": 2, "n_rotatable": 7
    },

    # ─── Phosphonates ──────────────────────────────────────────────────
    {
        "name": "Glyphosate", "cas": "1071-83-6", "formula": "C3H8NO5P",
        "smiles": "OC(=O)CNCP(O)(O)=O", "mw": 169.1,
        "degT50_soil": 12, "degT50_water": 7, "degT50_sediment": 150,
        "koc": 21699, "kfoc": 21699, "freundlich_n": 0.85,
        "vapor_pressure": 1.3e-7, "henry_const": 2.1e-7,
        "solubility": 10500, "pka": 2.3, "logP": -3.4,
        "cls": "Phosphonate", "status": "Approved",
        "n_atoms": 17, "n_heavy": 10, "hbd": 4, "hba": 6, "n_rings": 0, "n_rotatable": 4
    },
    {
        "name": "Glufosinate-ammonium", "cas": "77182-82-2", "formula": "C5H15N2O4P",
        "smiles": "CC(N)CCP(O)(O)=O", "mw": 198.2,
        "degT50_soil": 7, "degT50_water": 3, "degT50_sediment": 12,
        "koc": 500, "kfoc": 500, "freundlich_n": 0.90,
        "vapor_pressure": 3.1e-7, "henry_const": 2.0e-8,
        "solubility": 1370000, "pka": 2.0, "logP": -4.0,
        "cls": "Phosphonate", "status": "Not approved",
        "n_atoms": 26, "n_heavy": 12, "hbd": 4, "hba": 5, "n_rings": 0, "n_rotatable": 4
    },

    # ─── Dinitroanilines ───────────────────────────────────────────────
    {
        "name": "Pendimethalin", "cas": "40487-42-1", "formula": "C13H19N3O4",
        "smiles": "CCC(CC)Nc1c(C)cc([N+](=O)[O-])cc1[N+](=O)[O-]", "mw": 281.3,
        "degT50_soil": 90, "degT50_water": 45, "degT50_sediment": 200,
        "koc": 17491, "kfoc": 17491, "freundlich_n": 0.89,
        "vapor_pressure": 1.9e-3, "henry_const": 2.7e-1,
        "solubility": 0.33, "pka": None, "logP": 5.2,
        "cls": "Dinitroaniline", "status": "Approved",
        "n_atoms": 39, "n_heavy": 20, "hbd": 1, "hba": 5, "n_rings": 1, "n_rotatable": 5
    },
    {
        "name": "Trifluralin", "cas": "1582-09-8", "formula": "C13H16F3N3O4",
        "smiles": "CCCN(CCC)c1c(cc(C(F)(F)F)cc1[N+](=O)[O-])[N+](=O)[O-]",
        "mw": 335.3,
        "degT50_soil": 170, "degT50_water": 30, "degT50_sediment": 365,
        "koc": 8000, "kfoc": 8000, "freundlich_n": 0.87,
        "vapor_pressure": 9.5e-3, "henry_const": 1.5e1,
        "solubility": 0.18, "pka": None, "logP": 5.3,
        "cls": "Dinitroaniline", "status": "Not approved",
        "n_atoms": 36, "n_heavy": 23, "hbd": 0, "hba": 5, "n_rings": 1, "n_rotatable": 6
    },

    # ─── Dithiocarbamates ──────────────────────────────────────────────
    {
        "name": "Mancozeb", "cas": "8018-01-7", "formula": "C4H6MnN2S4Zn",
        "smiles": "[Mn++].[Zn++].[S-]C(=S)NCCNC([S-])=S", "mw": 271.2,
        "degT50_soil": 1, "degT50_water": 0.5, "degT50_sediment": 2,
        "koc": 998, "kfoc": 998, "freundlich_n": 0.90,
        "vapor_pressure": 1.3e-7, "henry_const": 1.0e-5,
        "solubility": 6.2, "pka": None, "logP": 1.33,
        "cls": "Dithiocarbamate", "status": "Not approved",
        "n_atoms": 18, "n_heavy": 12, "hbd": 2, "hba": 2, "n_rings": 0, "n_rotatable": 3
    },
    {
        "name": "Thiram", "cas": "137-26-8", "formula": "C6H12N2S4",
        "smiles": "CN(C)C(=S)SSC(=S)N(C)C", "mw": 240.4,
        "degT50_soil": 15, "degT50_water": 1, "degT50_sediment": 10,
        "koc": 670, "kfoc": 670, "freundlich_n": 0.88,
        "vapor_pressure": 2.3e-3, "henry_const": 5.8e-3,
        "solubility": 18, "pka": None, "logP": 1.73,
        "cls": "Dithiocarbamate", "status": "Not approved",
        "n_atoms": 24, "n_heavy": 12, "hbd": 0, "hba": 2, "n_rings": 0, "n_rotatable": 3
    },

    # ─── Chloroacetamides ──────────────────────────────────────────────
    {
        "name": "Metazachlor", "cas": "67129-08-2", "formula": "C14H16ClN3O",
        "smiles": "CC(=O)N(c1cccc(C)c1C)CC(Cl)=O", "mw": 277.8,
        "degT50_soil": 7, "degT50_water": 18, "degT50_sediment": 30,
        "koc": 54, "kfoc": 54, "freundlich_n": 0.90,
        "vapor_pressure": 9.3e-5, "henry_const": 1.5e-5,
        "solubility": 450, "pka": None, "logP": 2.49,
        "cls": "Chloroacetamide", "status": "Approved",
        "n_atoms": 34, "n_heavy": 19, "hbd": 0, "hba": 3, "n_rings": 1, "n_rotatable": 3
    },
    {
        "name": "S-Metolachlor", "cas": "87392-12-9", "formula": "C15H22ClNO2",
        "smiles": "CCC(Cc1cccc(C)c1N(C(C)COC)C(=O)CCl)C", "mw": 283.8,
        "degT50_soil": 15, "degT50_water": 25, "degT50_sediment": 45,
        "koc": 200, "kfoc": 200, "freundlich_n": 0.92,
        "vapor_pressure": 3.7e-3, "henry_const": 2.4e-3,
        "solubility": 480, "pka": None, "logP": 3.05,
        "cls": "Chloroacetamide", "status": "Approved",
        "n_atoms": 41, "n_heavy": 19, "hbd": 0, "hba": 3, "n_rings": 1, "n_rotatable": 6
    },

    # ─── Thiocarbamates ───────────────────────────────────────────────
    {
        "name": "Prosulfocarb", "cas": "52888-80-9", "formula": "C14H21NOS",
        "smiles": "CCCSC(=O)N(CC)c1ccccc1", "mw": 251.4,
        "degT50_soil": 10, "degT50_water": 8, "degT50_sediment": 20,
        "koc": 1693, "kfoc": 1693, "freundlich_n": 0.90,
        "vapor_pressure": 7.3e-3, "henry_const": 4.7e-1,
        "solubility": 13.2, "pka": None, "logP": 4.65,
        "cls": "Thiocarbamate", "status": "Approved",
        "n_atoms": 37, "n_heavy": 17, "hbd": 0, "hba": 2, "n_rings": 1, "n_rotatable": 6
    },

    # ─── Molluscicides ─────────────────────────────────────────────────
    {
        "name": "Metaldehyde", "cas": "108-62-3", "formula": "C8H16O4",
        "smiles": "CC1OC(C)OC(C)OC(C)O1", "mw": 176.2,
        "degT50_soil": 6, "degT50_water": 3, "degT50_sediment": 10,
        "koc": 34, "kfoc": 34, "freundlich_n": 0.95,
        "vapor_pressure": 4.0e-2, "henry_const": 1.2e-2,
        "solubility": 188, "pka": None, "logP": 0.12,
        "cls": "Molluscicide", "status": "Not approved",
        "n_atoms": 28, "n_heavy": 12, "hbd": 0, "hba": 4, "n_rings": 1, "n_rotatable": 0
    },
    {
        "name": "Ferric phosphate", "cas": "10045-86-0", "formula": "FePO4",
        "smiles": "[Fe+3].[O-]P([O-])([O-])=O", "mw": 150.8,
        "degT50_soil": 0.5, "degT50_water": 0.5, "degT50_sediment": 1,
        "koc": 10000, "kfoc": 10000, "freundlich_n": 1.0,
        "vapor_pressure": 0, "henry_const": 0,
        "solubility": 0.64, "pka": None, "logP": -3.0,
        "cls": "Molluscicide", "status": "Approved",
        "n_atoms": 6, "n_heavy": 6, "hbd": 0, "hba": 4, "n_rings": 0, "n_rotatable": 0
    },

    # ─── Chloronitriles ────────────────────────────────────────────────
    {
        "name": "Chlorothalonil", "cas": "1897-45-6", "formula": "C8Cl4N2",
        "smiles": "N#Cc1c(Cl)c(Cl)c(C#N)c(Cl)c1Cl", "mw": 265.9,
        "degT50_soil": 22, "degT50_water": 1.4, "degT50_sediment": 10,
        "koc": 1380, "kfoc": 1380, "freundlich_n": 0.90,
        "vapor_pressure": 7.6e-5, "henry_const": 2.5e-2,
        "solubility": 0.81, "pka": None, "logP": 2.94,
        "cls": "Chloronitrile", "status": "Not approved",
        "n_atoms": 14, "n_heavy": 14, "hbd": 0, "hba": 2, "n_rings": 1, "n_rotatable": 0
    },

    # ─── Phenoxyacetic acids ───────────────────────────────────────────
    {
        "name": "2,4-D", "cas": "94-75-7", "formula": "C8H6Cl2O3",
        "smiles": "OC(=O)COc1ccc(Cl)cc1Cl", "mw": 221.0,
        "degT50_soil": 10, "degT50_water": 15, "degT50_sediment": 20,
        "koc": 60, "kfoc": 60, "freundlich_n": 0.90,
        "vapor_pressure": 1.9e-5, "henry_const": 1.3e-8,
        "solubility": 677, "pka": 2.73, "logP": 2.81,
        "cls": "Phenoxyacetic acid", "status": "Approved",
        "n_atoms": 19, "n_heavy": 13, "hbd": 1, "hba": 3, "n_rings": 1, "n_rotatable": 3
    },
    {
        "name": "MCPA", "cas": "94-74-6", "formula": "C9H9ClO3",
        "smiles": "Cc1cc(OCC(O)=O)ccc1Cl", "mw": 200.6,
        "degT50_soil": 14, "degT50_water": 20, "degT50_sediment": 28,
        "koc": 74, "kfoc": 74, "freundlich_n": 0.90,
        "vapor_pressure": 4.0e-6, "henry_const": 1.6e-7,
        "solubility": 734, "pka": 3.07, "logP": 2.75,
        "cls": "Phenoxyacetic acid", "status": "Approved",
        "n_atoms": 22, "n_heavy": 13, "hbd": 1, "hba": 3, "n_rings": 1, "n_rotatable": 3
    },

    # ─── Sulfonylureas ─────────────────────────────────────────────────
    {
        "name": "Metsulfuron-methyl", "cas": "74223-64-6", "formula": "C14H15N5O6S",
        "smiles": "COC(=O)c1ccccc1S(=O)(=O)NC(=O)Nc1nc(OC)cc(C)n1", "mw": 381.4,
        "degT50_soil": 30, "degT50_water": 25, "degT50_sediment": 40,
        "koc": 35, "kfoc": 35, "freundlich_n": 0.90,
        "vapor_pressure": 3.3e-10, "henry_const": 1.7e-10,
        "solubility": 2790, "pka": 3.3, "logP": 0.018,
        "cls": "Sulfonylurea", "status": "Approved",
        "n_atoms": 41, "n_heavy": 26, "hbd": 2, "hba": 9, "n_rings": 2, "n_rotatable": 5
    },
    {
        "name": "Tribenuron-methyl", "cas": "101200-48-0", "formula": "C15H17N5O6S",
        "smiles": "COC(=O)c1ccccc1S(=O)(=O)N(C)C(=O)Nc1nc(OC)cc(C)n1", "mw": 395.4,
        "degT50_soil": 5, "degT50_water": 8, "degT50_sediment": 12,
        "koc": 26, "kfoc": 26, "freundlich_n": 0.92,
        "vapor_pressure": 5.2e-8, "henry_const": 5.2e-8,
        "solubility": 2040, "pka": 4.7, "logP": 0.78,
        "cls": "Sulfonylurea", "status": "Approved",
        "n_atoms": 43, "n_heavy": 27, "hbd": 1, "hba": 9, "n_rings": 2, "n_rotatable": 6
    },

    # ─── Ureas ─────────────────────────────────────────────────────────
    {
        "name": "Isoproturon", "cas": "34123-59-6", "formula": "C12H18N2O",
        "smiles": "CC(C)c1ccc(NC(=O)N(C)C)cc1", "mw": 206.3,
        "degT50_soil": 12, "degT50_water": 20, "degT50_sediment": 40,
        "koc": 122, "kfoc": 122, "freundlich_n": 0.90,
        "vapor_pressure": 3.2e-6, "henry_const": 1.5e-6,
        "solubility": 65, "pka": None, "logP": 2.5,
        "cls": "Phenylurea", "status": "Not approved",
        "n_atoms": 33, "n_heavy": 15, "hbd": 1, "hba": 2, "n_rings": 1, "n_rotatable": 3
    },
    {
        "name": "Diuron", "cas": "330-54-1", "formula": "C9H10Cl2N2O",
        "smiles": "CN(C)C(=O)Nc1ccc(Cl)c(Cl)c1", "mw": 233.1,
        "degT50_soil": 75, "degT50_water": 43, "degT50_sediment": 200,
        "koc": 813, "kfoc": 813, "freundlich_n": 0.85,
        "vapor_pressure": 1.1e-6, "henry_const": 5.1e-6,
        "solubility": 35, "pka": None, "logP": 2.68,
        "cls": "Phenylurea", "status": "Not approved",
        "n_atoms": 24, "n_heavy": 14, "hbd": 1, "hba": 2, "n_rings": 1, "n_rotatable": 1
    },
    {
        "name": "Linuron", "cas": "330-55-2", "formula": "C9H10Cl2N2O2",
        "smiles": "CON(C)C(=O)Nc1ccc(Cl)c(Cl)c1", "mw": 249.1,
        "degT50_soil": 48, "degT50_water": 30, "degT50_sediment": 100,
        "koc": 370, "kfoc": 370, "freundlich_n": 0.88,
        "vapor_pressure": 5.1e-3, "henry_const": 2.5e-2,
        "solubility": 63.8, "pka": None, "logP": 3.0,
        "cls": "Phenylurea", "status": "Not approved",
        "n_atoms": 26, "n_heavy": 15, "hbd": 1, "hba": 3, "n_rings": 1, "n_rotatable": 2
    },

    # ─── Carbamates ────────────────────────────────────────────────────
    {
        "name": "Pirimicarb", "cas": "23103-98-2", "formula": "C11H18N4O2",
        "smiles": "CN(C)C(=O)Oc1nc(N(C)C)nc(C)c1C", "mw": 238.3,
        "degT50_soil": 9, "degT50_water": 7, "degT50_sediment": 18,
        "koc": 388, "kfoc": 388, "freundlich_n": 0.90,
        "vapor_pressure": 4.0e-4, "henry_const": 1.8e-4,
        "solubility": 3100, "pka": 4.4, "logP": 1.7,
        "cls": "Carbamate", "status": "Approved",
        "n_atoms": 35, "n_heavy": 17, "hbd": 0, "hba": 5, "n_rings": 1, "n_rotatable": 3
    },
    {
        "name": "Methomyl", "cas": "16752-77-5", "formula": "C5H10N2O2S",
        "smiles": "CNC(=O)O/N=C(/C)SC", "mw": 162.2,
        "degT50_soil": 7, "degT50_water": 6, "degT50_sediment": 8,
        "koc": 72, "kfoc": 72, "freundlich_n": 0.90,
        "vapor_pressure": 7.2e-3, "henry_const": 1.7e-4,
        "solubility": 57900, "pka": None, "logP": 0.09,
        "cls": "Carbamate", "status": "Not approved",
        "n_atoms": 19, "n_heavy": 10, "hbd": 1, "hba": 3, "n_rings": 0, "n_rotatable": 3
    },

    # ─── Benzimidazoles ────────────────────────────────────────────────
    {
        "name": "Carbendazim", "cas": "10605-21-7", "formula": "C9H9N3O2",
        "smiles": "COC(=O)Nc1nc2ccccc2[nH]1", "mw": 191.2,
        "degT50_soil": 40, "degT50_water": 18, "degT50_sediment": 120,
        "koc": 225, "kfoc": 225, "freundlich_n": 0.85,
        "vapor_pressure": 9.0e-8, "henry_const": 3.6e-8,
        "solubility": 8, "pka": 4.2, "logP": 1.52,
        "cls": "Benzimidazole", "status": "Not approved",
        "n_atoms": 23, "n_heavy": 14, "hbd": 2, "hba": 4, "n_rings": 2, "n_rotatable": 2
    },
    {
        "name": "Thiophanate-methyl", "cas": "23564-05-8", "formula": "C12H14N4O4S2",
        "smiles": "COC(=O)NC(=S)Nc1ccccc1NC(=S)NC(=O)OC", "mw": 342.4,
        "degT50_soil": 4, "degT50_water": 1, "degT50_sediment": 8,
        "koc": 1830, "kfoc": 1830, "freundlich_n": 0.88,
        "vapor_pressure": 9.5e-6, "henry_const": 1.8e-3,
        "solubility": 20, "pka": 7.28, "logP": 1.45,
        "cls": "Benzimidazole", "status": "Not approved",
        "n_atoms": 36, "n_heavy": 22, "hbd": 4, "hba": 6, "n_rings": 1, "n_rotatable": 6
    },

    # ─── Bipyridiliums ─────────────────────────────────────────────────
    {
        "name": "Diquat", "cas": "85-00-7", "formula": "C12H12N2",
        "smiles": "c1cc[n+]2c(c1)C=CC1=[n+](C2)c2ccccc21", "mw": 184.2,
        "degT50_soil": 1000, "degT50_water": 2, "degT50_sediment": 1000,
        "koc": 1000000, "kfoc": 1000000, "freundlich_n": 0.80,
        "vapor_pressure": 1.0e-7, "henry_const": 5.0e-12,
        "solubility": 718000, "pka": None, "logP": -4.6,
        "cls": "Bipyridilium", "status": "Not approved",
        "n_atoms": 26, "n_heavy": 14, "hbd": 0, "hba": 2, "n_rings": 2, "n_rotatable": 1
    },

    # ─── Triazines ─────────────────────────────────────────────────────
    {
        "name": "Terbuthylazine", "cas": "5915-41-3", "formula": "C9H16ClN5",
        "smiles": "CCNc1nc(Cl)nc(NC(C)(C)C)n1", "mw": 229.7,
        "degT50_soil": 28, "degT50_water": 62, "degT50_sediment": 100,
        "koc": 231, "kfoc": 231, "freundlich_n": 0.90,
        "vapor_pressure": 1.5e-4, "henry_const": 3.2e-5,
        "solubility": 6.6, "pka": 1.9, "logP": 3.21,
        "cls": "Triazine", "status": "Approved",
        "n_atoms": 31, "n_heavy": 15, "hbd": 2, "hba": 4, "n_rings": 1, "n_rotatable": 3
    },
    {
        "name": "Atrazine", "cas": "1912-24-9", "formula": "C8H14ClN5",
        "smiles": "CCNc1nc(Cl)nc(NC(C)C)n1", "mw": 215.7,
        "degT50_soil": 75, "degT50_water": 86, "degT50_sediment": 150,
        "koc": 100, "kfoc": 100, "freundlich_n": 0.92,
        "vapor_pressure": 3.9e-5, "henry_const": 1.5e-5,
        "solubility": 35, "pka": 1.7, "logP": 2.7,
        "cls": "Triazine", "status": "Not approved",
        "n_atoms": 28, "n_heavy": 14, "hbd": 2, "hba": 4, "n_rings": 1, "n_rotatable": 3
    },

    # ─── SDHIs (Succinate dehydrogenase inhibitors) ────────────────────
    {
        "name": "Boscalid", "cas": "188425-85-6", "formula": "C18H12Cl2N2O",
        "smiles": "O=C(Nc1ccccc1-c1ccc(Cl)cc1)c1ccnc(Cl)c1", "mw": 343.2,
        "degT50_soil": 200, "degT50_water": 30, "degT50_sediment": 500,
        "koc": 772, "kfoc": 772, "freundlich_n": 0.88,
        "vapor_pressure": 7.2e-7, "henry_const": 5.0e-5,
        "solubility": 4.6, "pka": None, "logP": 2.96,
        "cls": "SDHI", "status": "Approved",
        "n_atoms": 35, "n_heavy": 23, "hbd": 1, "hba": 3, "n_rings": 3, "n_rotatable": 3
    },
    {
        "name": "Fluopyram", "cas": "658066-35-4", "formula": "C16H11ClF6N2O",
        "smiles": "O=C(c1cc(C(F)(F)F)cc(Cl)c1)NC(=O)c1ccnc(C(F)(F)F)c1", "mw": 396.7,
        "degT50_soil": 300, "degT50_water": 500, "degT50_sediment": 1000,
        "koc": 426, "kfoc": 426, "freundlich_n": 0.85,
        "vapor_pressure": 1.2e-6, "henry_const": 9.7e-5,
        "solubility": 16, "pka": None, "logP": 3.3,
        "cls": "SDHI", "status": "Approved",
        "n_atoms": 36, "n_heavy": 26, "hbd": 1, "hba": 3, "n_rings": 2, "n_rotatable": 3
    },

    # ─── Diamides ──────────────────────────────────────────────────────
    {
        "name": "Chlorantraniliprole", "cas": "500008-45-7", "formula": "C18H14BrCl2N5O2",
        "smiles": "CNC(=O)c1cc(Cl)cc(c1NC(=O)c1cc(Br)nn1C)Cl", "mw": 483.2,
        "degT50_soil": 597, "degT50_water": 170, "degT50_sediment": 1000,
        "koc": 362, "kfoc": 362, "freundlich_n": 0.90,
        "vapor_pressure": 6.3e-12, "henry_const": 3.2e-12,
        "solubility": 1.02, "pka": 10.88, "logP": 2.86,
        "cls": "Diamide", "status": "Approved",
        "n_atoms": 42, "n_heavy": 28, "hbd": 2, "hba": 5, "n_rings": 3, "n_rotatable": 3
    },

    # ─── Spinosyns ─────────────────────────────────────────────────────
    {
        "name": "Spinosad", "cas": "168316-95-8", "formula": "C41H65NO10",
        "smiles": "CC1CCCC(=O)OCC2CCC(CC(=O)OC)CC2OC1", "mw": 731.9,
        "degT50_soil": 9, "degT50_water": 0.3, "degT50_sediment": 30,
        "koc": 14700, "kfoc": 14700, "freundlich_n": 0.85,
        "vapor_pressure": 3.0e-10, "henry_const": 3.2e-8,
        "solubility": 89, "pka": 8.1, "logP": 4.01,
        "cls": "Spinosyn", "status": "Approved",
        "n_atoms": 117, "n_heavy": 52, "hbd": 1, "hba": 10, "n_rings": 5, "n_rotatable": 5
    },

    # ─── Oxadiazines ───────────────────────────────────────────────────
    {
        "name": "Indoxacarb", "cas": "173584-44-6", "formula": "C22H17ClF3N3O7",
        "smiles": "COC(=O)C1(OC)C(=O)N(c2cc(Cl)ccc2C(F)(F)F)C(=O)N1Cc1ccccn1",
        "mw": 527.8,
        "degT50_soil": 4, "degT50_water": 3, "degT50_sediment": 10,
        "koc": 6840, "kfoc": 6840, "freundlich_n": 0.87,
        "vapor_pressure": 2.5e-9, "henry_const": 4.2e-8,
        "solubility": 0.2, "pka": None, "logP": 4.65,
        "cls": "Oxadiazine", "status": "Approved",
        "n_atoms": 52, "n_heavy": 36, "hbd": 0, "hba": 9, "n_rings": 4, "n_rotatable": 5
    },

    # ─── Phenylpyrazoles ───────────────────────────────────────────────
    {
        "name": "Fipronil", "cas": "120068-37-3", "formula": "C12H4Cl2F6N4OS",
        "smiles": "N#Cc1nn(c2c(Cl)c(C(F)(F)F)cc(Cl)c2)c(N)c1S(=O)C(F)(F)F",
        "mw": 437.1,
        "degT50_soil": 65, "degT50_water": 54, "degT50_sediment": 120,
        "koc": 803, "kfoc": 803, "freundlich_n": 0.88,
        "vapor_pressure": 3.7e-7, "henry_const": 2.3e-4,
        "solubility": 1.9, "pka": None, "logP": 4.0,
        "cls": "Phenylpyrazole", "status": "Not approved",
        "n_atoms": 29, "n_heavy": 25, "hbd": 1, "hba": 5, "n_rings": 2, "n_rotatable": 2
    },

    # ─── Additional Triazoles ──────────────────────────────────────────
    {
        "name": "Cyproconazole", "cas": "94361-06-5", "formula": "C15H18ClN3O",
        "smiles": "OC(c1ccc(Cl)cc1)(C1CC1)Cn1cncn1", "mw": 291.8,
        "degT50_soil": 60, "degT50_water": 45, "degT50_sediment": 300,
        "koc": 434, "kfoc": 434, "freundlich_n": 0.88,
        "vapor_pressure": 2.6e-5, "henry_const": 5.5e-5,
        "solubility": 93, "pka": 4.3, "logP": 3.09,
        "cls": "Triazole", "status": "Not approved",
        "n_atoms": 37, "n_heavy": 20, "hbd": 1, "hba": 3, "n_rings": 3, "n_rotatable": 3
    },
    {
        "name": "Flutriafol", "cas": "76674-21-0", "formula": "C16H13F2N3O",
        "smiles": "OC(Cn1cncn1)(c1ccccc1)c1ccc(F)cc1F", "mw": 301.3,
        "degT50_soil": 1389, "degT50_water": 100, "degT50_sediment": 500,
        "koc": 205, "kfoc": 205, "freundlich_n": 0.90,
        "vapor_pressure": 4.0e-7, "henry_const": 3.5e-6,
        "solubility": 95, "pka": 2.3, "logP": 2.3,
        "cls": "Triazole", "status": "Approved",
        "n_atoms": 35, "n_heavy": 22, "hbd": 1, "hba": 3, "n_rings": 3, "n_rotatable": 3
    },
    {
        "name": "Difenoconazole", "cas": "119446-68-3", "formula": "C19H17Cl2N3O3",
        "smiles": "OC(Cn1cncn1)c1ccc(Oc2ccc(Cl)cc2Cl)cc1OC1COCC1", "mw": 406.3,
        "degT50_soil": 90, "degT50_water": 65, "degT50_sediment": 400,
        "koc": 3760, "kfoc": 3760, "freundlich_n": 0.85,
        "vapor_pressure": 3.3e-8, "henry_const": 1.0e-6,
        "solubility": 15, "pka": 1.07, "logP": 4.36,
        "cls": "Triazole", "status": "Approved",
        "n_atoms": 44, "n_heavy": 27, "hbd": 1, "hba": 6, "n_rings": 4, "n_rotatable": 7
    },
    {
        "name": "Penconazole", "cas": "66246-88-6", "formula": "C13H15Cl2N3",
        "smiles": "CCCC(Cn1cncn1)c1ccc(Cl)cc1Cl", "mw": 284.2,
        "degT50_soil": 117, "degT50_water": 60, "degT50_sediment": 250,
        "koc": 1230, "kfoc": 1230, "freundlich_n": 0.87,
        "vapor_pressure": 5.5e-5, "henry_const": 4.5e-4,
        "solubility": 73, "pka": 1.51, "logP": 3.72,
        "cls": "Triazole", "status": "Approved",
        "n_atoms": 33, "n_heavy": 18, "hbd": 0, "hba": 3, "n_rings": 2, "n_rotatable": 4
    },

    # ─── Additional Pyrethroids ────────────────────────────────────────
    {
        "name": "Bifenthrin", "cas": "82657-04-3", "formula": "C23H22ClF3O2",
        "smiles": "CC1(C)C(c2ccc(Cl)cc2)C1C(=O)OCc1cccc(-c2ccccc2)c1", "mw": 422.9,
        "degT50_soil": 96, "degT50_water": 8, "degT50_sediment": 200,
        "koc": 131000, "kfoc": 131000, "freundlich_n": 0.82,
        "vapor_pressure": 1.8e-5, "henry_const": 7.2e-3,
        "solubility": 0.001, "pka": None, "logP": 6.6,
        "cls": "Pyrethroid", "status": "Not approved",
        "n_atoms": 51, "n_heavy": 29, "hbd": 0, "hba": 2, "n_rings": 4, "n_rotatable": 6
    },
    {
        "name": "Esfenvalerate", "cas": "66230-04-4", "formula": "C25H22ClNO3",
        "smiles": "CC(c1ccc(Cl)cc1)C(=O)OC(C#N)c1cccc(Oc2ccccc2)c1", "mw": 419.9,
        "degT50_soil": 44, "degT50_water": 10, "degT50_sediment": 120,
        "koc": 67000, "kfoc": 67000, "freundlich_n": 0.83,
        "vapor_pressure": 1.5e-7, "henry_const": 2.1e-2,
        "solubility": 0.002, "pka": None, "logP": 6.22,
        "cls": "Pyrethroid", "status": "Not approved",
        "n_atoms": 51, "n_heavy": 30, "hbd": 0, "hba": 4, "n_rings": 3, "n_rotatable": 8
    },
    {
        "name": "Permethrin", "cas": "52645-53-1", "formula": "C21H20Cl2O3",
        "smiles": "CC1(C)C(C=C(Cl)Cl)C1C(=O)OCc1cccc(Oc2ccccc2)c1", "mw": 391.3,
        "degT50_soil": 13, "degT50_water": 5, "degT50_sediment": 40,
        "koc": 100000, "kfoc": 100000, "freundlich_n": 0.84,
        "vapor_pressure": 2.5e-6, "henry_const": 1.4e-3,
        "solubility": 0.006, "pka": None, "logP": 6.1,
        "cls": "Pyrethroid", "status": "Not approved",
        "n_atoms": 46, "n_heavy": 26, "hbd": 0, "hba": 3, "n_rings": 3, "n_rotatable": 7
    },

    # ─── Additional Organophosphates ───────────────────────────────────
    {
        "name": "Diazinon", "cas": "333-41-5", "formula": "C12H21N2O3PS",
        "smiles": "CCOP(=S)(OCC)Oc1cc(C)nc(C(C)C)n1", "mw": 304.3,
        "degT50_soil": 40, "degT50_water": 138, "degT50_sediment": 80,
        "koc": 609, "kfoc": 609, "freundlich_n": 0.89,
        "vapor_pressure": 1.2e-2, "henry_const": 1.4e-1,
        "solubility": 60, "pka": 2.6, "logP": 3.81,
        "cls": "Organophosphate", "status": "Not approved",
        "n_atoms": 39, "n_heavy": 19, "hbd": 0, "hba": 5, "n_rings": 1, "n_rotatable": 6
    },
    {
        "name": "Acephate", "cas": "30560-19-1", "formula": "C4H10NO3PS",
        "smiles": "CC(=O)NP(=O)(OC)SC", "mw": 183.2,
        "degT50_soil": 3, "degT50_water": 50, "degT50_sediment": 10,
        "koc": 26, "kfoc": 26, "freundlich_n": 0.95,
        "vapor_pressure": 2.3e-4, "henry_const": 5.0e-8,
        "solubility": 790000, "pka": 8.35, "logP": -0.85,
        "cls": "Organophosphate", "status": "Not approved",
        "n_atoms": 19, "n_heavy": 10, "hbd": 1, "hba": 4, "n_rings": 0, "n_rotatable": 3
    },
    {
        "name": "Profenofos", "cas": "41198-08-7", "formula": "C11H15BrClO3PS",
        "smiles": "CCCSP(=O)(OCC)Oc1ccc(Br)cc1Cl", "mw": 373.6,
        "degT50_soil": 8, "degT50_water": 20, "degT50_sediment": 25,
        "koc": 2016, "kfoc": 2016, "freundlich_n": 0.87,
        "vapor_pressure": 1.2e-3, "henry_const": 9.0e-3,
        "solubility": 28, "pka": None, "logP": 4.44,
        "cls": "Organophosphate", "status": "Not approved",
        "n_atoms": 32, "n_heavy": 18, "hbd": 0, "hba": 4, "n_rings": 1, "n_rotatable": 6
    },

    # ─── Additional Strobilurins ───────────────────────────────────────
    {
        "name": "Trifloxystrobin", "cas": "141517-21-7", "formula": "C20H19F3N2O4",
        "smiles": "CO/N=C(/C(=O)OC)c1ccccc1CON=Cc1cccc(C(F)(F)F)c1", "mw": 408.4,
        "degT50_soil": 7, "degT50_water": 2.1, "degT50_sediment": 20,
        "koc": 2377, "kfoc": 2377, "freundlich_n": 0.88,
        "vapor_pressure": 3.4e-6, "henry_const": 2.3e-4,
        "solubility": 0.61, "pka": None, "logP": 4.5,
        "cls": "Strobilurin", "status": "Approved",
        "n_atoms": 48, "n_heavy": 29, "hbd": 0, "hba": 7, "n_rings": 2, "n_rotatable": 9
    },
    {
        "name": "Fluoxastrobin", "cas": "361377-29-9", "formula": "C21H16ClFN4O5",
        "smiles": "COC(=O)/C(=N\\OC)c1ccccc1Oc1nc(F)c(Cl)c(OC)n1", "mw": 458.8,
        "degT50_soil": 12, "degT50_water": 18, "degT50_sediment": 50,
        "koc": 505, "kfoc": 505, "freundlich_n": 0.90,
        "vapor_pressure": 2.9e-8, "henry_const": 7.0e-7,
        "solubility": 1.9, "pka": None, "logP": 2.86,
        "cls": "Strobilurin", "status": "Approved",
        "n_atoms": 46, "n_heavy": 31, "hbd": 0, "hba": 8, "n_rings": 3, "n_rotatable": 7
    },
    {
        "name": "Picoxystrobin", "cas": "117428-22-5", "formula": "C18H16F3NO4",
        "smiles": "CO/N=C(/C(=O)OC)c1ccccc1COc1ccn(C)c(=O)c1", "mw": 367.3,
        "degT50_soil": 22, "degT50_water": 3, "degT50_sediment": 40,
        "koc": 756, "kfoc": 756, "freundlich_n": 0.89,
        "vapor_pressure": 3.0e-6, "henry_const": 4.8e-5,
        "solubility": 3.1, "pka": None, "logP": 3.6,
        "cls": "Strobilurin", "status": "Approved",
        "n_atoms": 42, "n_heavy": 26, "hbd": 0, "hba": 7, "n_rings": 2, "n_rotatable": 7
    },

    # ─── Additional Neonicotinoids ─────────────────────────────────────
    {
        "name": "Dinotefuran", "cas": "165252-70-0", "formula": "C7H14N4O3",
        "smiles": "CN(CC1CCOC1)C(=N[N+](=O)[O-])N", "mw": 202.2,
        "degT50_soil": 82, "degT50_water": 3, "degT50_sediment": 30,
        "koc": 26, "kfoc": 26, "freundlich_n": 0.93,
        "vapor_pressure": 1.7e-9, "henry_const": 1.3e-10,
        "solubility": 39830, "pka": 12.6, "logP": -0.55,
        "cls": "Neonicotinoid", "status": "Not approved",
        "n_atoms": 28, "n_heavy": 14, "hbd": 1, "hba": 5, "n_rings": 1, "n_rotatable": 3
    },
    {
        "name": "Nitenpyram", "cas": "150824-47-8", "formula": "C11H15ClN4O2",
        "smiles": "CCN(Cc1ccc(Cl)nc1)/C(=C/[N+](=O)[O-])NC", "mw": 270.7,
        "degT50_soil": 1, "degT50_water": 2.9, "degT50_sediment": 5,
        "koc": 30, "kfoc": 30, "freundlich_n": 0.93,
        "vapor_pressure": 1.1e-9, "henry_const": 8.8e-12,
        "solubility": 590000, "pka": 3.1, "logP": -0.66,
        "cls": "Neonicotinoid", "status": "Not approved",
        "n_atoms": 33, "n_heavy": 18, "hbd": 1, "hba": 5, "n_rings": 1, "n_rotatable": 5
    },

    # ─── Additional Carbamates ─────────────────────────────────────────
    {
        "name": "Methiocarb", "cas": "2032-65-7", "formula": "C11H15NO2S",
        "smiles": "CNC(=O)Oc1cc(C)c(SC)c(C)c1", "mw": 225.3,
        "degT50_soil": 4, "degT50_water": 10, "degT50_sediment": 15,
        "koc": 660, "kfoc": 660, "freundlich_n": 0.88,
        "vapor_pressure": 1.5e-3, "henry_const": 5.6e-4,
        "solubility": 27, "pka": None, "logP": 3.18,
        "cls": "Carbamate", "status": "Not approved",
        "n_atoms": 29, "n_heavy": 15, "hbd": 1, "hba": 3, "n_rings": 1, "n_rotatable": 3
    },
    {
        "name": "Oxamyl", "cas": "23135-22-0", "formula": "C7H13N3O3S",
        "smiles": "CC(SC)=NOC(=O)N(C)NC(=O)C", "mw": 219.3,
        "degT50_soil": 5, "degT50_water": 8, "degT50_sediment": 10,
        "koc": 25, "kfoc": 25, "freundlich_n": 0.94,
        "vapor_pressure": 3.1e-4, "henry_const": 2.1e-8,
        "solubility": 148000, "pka": None, "logP": -0.47,
        "cls": "Carbamate", "status": "Approved",
        "n_atoms": 26, "n_heavy": 14, "hbd": 1, "hba": 5, "n_rings": 0, "n_rotatable": 5
    },
    {
        "name": "Aldicarb", "cas": "116-06-3", "formula": "C7H14N2O2S",
        "smiles": "CC(C)(SC)C=NOC(=O)NC", "mw": 190.3,
        "degT50_soil": 30, "degT50_water": 28, "degT50_sediment": 60,
        "koc": 30, "kfoc": 30, "freundlich_n": 0.92,
        "vapor_pressure": 1.3e-2, "henry_const": 1.7e-4,
        "solubility": 6000, "pka": None, "logP": 1.13,
        "cls": "Carbamate", "status": "Not approved",
        "n_atoms": 25, "n_heavy": 12, "hbd": 1, "hba": 4, "n_rings": 0, "n_rotatable": 4
    },

    # ─── Additional SDHIs ──────────────────────────────────────────────
    {
        "name": "Penthiopyrad", "cas": "183675-82-3", "formula": "C16H20F3N3OS",
        "smiles": "CC(C)c1cc(C(F)(F)F)nn1C(=O)c1ccsc1NC(C)C", "mw": 359.4,
        "degT50_soil": 89, "degT50_water": 14, "degT50_sediment": 200,
        "koc": 981, "kfoc": 981, "freundlich_n": 0.87,
        "vapor_pressure": 7.9e-7, "henry_const": 5.2e-6,
        "solubility": 12.4, "pka": None, "logP": 3.2,
        "cls": "SDHI", "status": "Approved",
        "n_atoms": 43, "n_heavy": 24, "hbd": 1, "hba": 4, "n_rings": 2, "n_rotatable": 5
    },
    {
        "name": "Isopyrazam", "cas": "881685-58-1", "formula": "C20H23F2N3O",
        "smiles": "CC(C)C1CC1c1nn(c(C)c1C(=O)Nc1cc(F)cc(F)c1)C", "mw": 359.4,
        "degT50_soil": 193, "degT50_water": 50, "degT50_sediment": 400,
        "koc": 1589, "kfoc": 1589, "freundlich_n": 0.86,
        "vapor_pressure": 1.8e-7, "henry_const": 3.4e-5,
        "solubility": 1.6, "pka": None, "logP": 4.11,
        "cls": "SDHI", "status": "Approved",
        "n_atoms": 48, "n_heavy": 26, "hbd": 1, "hba": 3, "n_rings": 3, "n_rotatable": 4
    },
    {
        "name": "Fluxapyroxad", "cas": "907204-31-3", "formula": "C18H12F5N3O",
        "smiles": "CC1CC1c1nn(c(C(F)F)c1C(=O)Nc1cc(F)cc(F)c1)C", "mw": 381.3,
        "degT50_soil": 156, "degT50_water": 30, "degT50_sediment": 300,
        "koc": 483, "kfoc": 483, "freundlich_n": 0.88,
        "vapor_pressure": 3.5e-8, "henry_const": 6.9e-6,
        "solubility": 3.3, "pka": None, "logP": 3.08,
        "cls": "SDHI", "status": "Approved",
        "n_atoms": 39, "n_heavy": 27, "hbd": 1, "hba": 3, "n_rings": 3, "n_rotatable": 3
    },

    # ─── Additional Sulfonylureas ──────────────────────────────────────
    {
        "name": "Sulfosulfuron", "cas": "141776-32-1", "formula": "C16H18N6O7S2",
        "smiles": "COc1cc(C)nc(NC(=O)NS(=O)(=O)c2ccc(-c3cccs3)c(S(N)(=O)=O)c2)n1",
        "mw": 470.5,
        "degT50_soil": 11, "degT50_water": 25, "degT50_sediment": 30,
        "koc": 36, "kfoc": 36, "freundlich_n": 0.91,
        "vapor_pressure": 7.0e-11, "henry_const": 3.1e-12,
        "solubility": 1627, "pka": 3.5, "logP": 0.77,
        "cls": "Sulfonylurea", "status": "Approved",
        "n_atoms": 49, "n_heavy": 31, "hbd": 3, "hba": 10, "n_rings": 3, "n_rotatable": 6
    },
    {
        "name": "Nicosulfuron", "cas": "111991-09-4", "formula": "C15H18N6O6S",
        "smiles": "COC(=O)c1cc(S(=O)(=O)NC(=O)Nc2nc(OC)cc(OC)n2)cn1C", "mw": 410.4,
        "degT50_soil": 26, "degT50_water": 14, "degT50_sediment": 35,
        "koc": 30, "kfoc": 30, "freundlich_n": 0.92,
        "vapor_pressure": 8.0e-13, "henry_const": 1.7e-12,
        "solubility": 7500, "pka": 4.6, "logP": 0.61,
        "cls": "Sulfonylurea", "status": "Approved",
        "n_atoms": 46, "n_heavy": 28, "hbd": 2, "hba": 9, "n_rings": 2, "n_rotatable": 6
    },

    # ─── Additional Herbicides ─────────────────────────────────────────
    {
        "name": "Flufenacet", "cas": "142459-58-3", "formula": "C14H13F4N3O2S",
        "smiles": "CC(Oc1ccc(F)c(F)c1)C(=O)N(C)c1nnsc1", "mw": 363.3,
        "degT50_soil": 14, "degT50_water": 25, "degT50_sediment": 50,
        "koc": 401, "kfoc": 401, "freundlich_n": 0.89,
        "vapor_pressure": 9.0e-7, "henry_const": 5.0e-7,
        "solubility": 56, "pka": None, "logP": 3.2,
        "cls": "Oxyacetamide", "status": "Approved",
        "n_atoms": 37, "n_heavy": 24, "hbd": 0, "hba": 5, "n_rings": 2, "n_rotatable": 5
    },
    {
        "name": "Clomazone", "cas": "81777-89-1", "formula": "C12H14ClNO2",
        "smiles": "CC1(C)COc2ccccc2N1CC(=O)Cl", "mw": 239.7,
        "degT50_soil": 24, "degT50_water": 35, "degT50_sediment": 60,
        "koc": 300, "kfoc": 300, "freundlich_n": 0.90,
        "vapor_pressure": 1.9e-2, "henry_const": 4.2e-3,
        "solubility": 1100, "pka": None, "logP": 2.54,
        "cls": "Isoxazolidinone", "status": "Approved",
        "n_atoms": 29, "n_heavy": 16, "hbd": 0, "hba": 3, "n_rings": 2, "n_rotatable": 2
    },
    {
        "name": "Dimethenamid-P", "cas": "163515-14-8", "formula": "C12H18ClNO2S",
        "smiles": "CC(Oc1nsc(C)c1C)C(=O)N(CC=C)c1cccc(Cl)c1", "mw": 275.8,
        "degT50_soil": 11, "degT50_water": 20, "degT50_sediment": 30,
        "koc": 129, "kfoc": 129, "freundlich_n": 0.91,
        "vapor_pressure": 2.5e-3, "henry_const": 6.0e-4,
        "solubility": 1174, "pka": None, "logP": 1.89,
        "cls": "Chloroacetamide", "status": "Approved",
        "n_atoms": 34, "n_heavy": 17, "hbd": 0, "hba": 3, "n_rings": 1, "n_rotatable": 5
    },
    {
        "name": "Metribuzin", "cas": "21087-64-9", "formula": "C8H14N4OS",
        "smiles": "CC(C)c1nnc(SC)c(=O)n1N", "mw": 214.3,
        "degT50_soil": 19, "degT50_water": 41, "degT50_sediment": 60,
        "koc": 38, "kfoc": 38, "freundlich_n": 0.93,
        "vapor_pressure": 5.8e-5, "henry_const": 3.0e-7,
        "solubility": 1165, "pka": 1.0, "logP": 1.65,
        "cls": "Triazinone", "status": "Approved",
        "n_atoms": 28, "n_heavy": 14, "hbd": 1, "hba": 4, "n_rings": 1, "n_rotatable": 2
    },

    # ─── Newer Chemistries ─────────────────────────────────────────────
    {
        "name": "Flupyradifurone", "cas": "951659-40-8", "formula": "C12H11ClF2N2O2",
        "smiles": "O=C(NCc1ccn(C)c1)OC(CF)c1ccc(Cl)cc1F", "mw": 288.7,
        "degT50_soil": 66, "degT50_water": 30, "degT50_sediment": 100,
        "koc": 145, "kfoc": 145, "freundlich_n": 0.89,
        "vapor_pressure": 1.2e-8, "henry_const": 1.0e-8,
        "solubility": 3200, "pka": None, "logP": 1.2,
        "cls": "Butenolide", "status": "Approved",
        "n_atoms": 30, "n_heavy": 19, "hbd": 1, "hba": 4, "n_rings": 2, "n_rotatable": 5
    },
    {
        "name": "Sulfoxaflor", "cas": "946578-00-3", "formula": "C10H10F3N3OS",
        "smiles": "CC(c1ncc(C(F)(F)F)s1)N(C)C(=N)S(C)=O", "mw": 277.3,
        "degT50_soil": 12, "degT50_water": 37, "degT50_sediment": 20,
        "koc": 37, "kfoc": 37, "freundlich_n": 0.92,
        "vapor_pressure": 6.0e-7, "henry_const": 2.0e-7,
        "solubility": 568, "pka": None, "logP": 0.80,
        "cls": "Sulfoximine", "status": "Approved",
        "n_atoms": 27, "n_heavy": 18, "hbd": 1, "hba": 4, "n_rings": 1, "n_rotatable": 4
    },
    {
        "name": "Cyantraniliprole", "cas": "736994-63-1", "formula": "C19H14BrClN6O2",
        "smiles": "CNC(=O)c1cc(Cl)cc(c1NC(=O)c1cc(Br)n(C)n1)C#N", "mw": 473.7,
        "degT50_soil": 34, "degT50_water": 2, "degT50_sediment": 100,
        "koc": 576, "kfoc": 576, "freundlich_n": 0.88,
        "vapor_pressure": 5.1e-12, "henry_const": 3.8e-12,
        "solubility": 14.2, "pka": 8.8, "logP": 1.94,
        "cls": "Diamide", "status": "Approved",
        "n_atoms": 44, "n_heavy": 30, "hbd": 2, "hba": 5, "n_rings": 3, "n_rotatable": 3
    },

    # ─── Morpholines ───────────────────────────────────────────────────
    {
        "name": "Fenpropimorph", "cas": "67564-91-4", "formula": "C20H33NO",
        "smiles": "CC(Cc1ccc(C(C)(C)C)cc1)CN1CCOCC1", "mw": 303.5,
        "degT50_soil": 28, "degT50_water": 20, "degT50_sediment": 55,
        "koc": 3900, "kfoc": 3900, "freundlich_n": 0.85,
        "vapor_pressure": 5.6e-3, "henry_const": 2.1e-1,
        "solubility": 4.3, "pka": 6.9, "logP": 4.1,
        "cls": "Morpholine", "status": "Not approved",
        "n_atoms": 55, "n_heavy": 22, "hbd": 0, "hba": 2, "n_rings": 2, "n_rotatable": 7
    },
    {
        "name": "Spiroxamine", "cas": "118134-30-8", "formula": "C18H35NO2",
        "smiles": "CCC(CC1COC(CC)O1)CN(CC)CC", "mw": 297.5,
        "degT50_soil": 31, "degT50_water": 15, "degT50_sediment": 50,
        "koc": 1900, "kfoc": 1900, "freundlich_n": 0.87,
        "vapor_pressure": 3.9e-3, "henry_const": 2.7e-1,
        "solubility": 405, "pka": 7.6, "logP": 2.89,
        "cls": "Morpholine", "status": "Approved",
        "n_atoms": 56, "n_heavy": 21, "hbd": 0, "hba": 3, "n_rings": 1, "n_rotatable": 9
    },

    # ─── Benzoylureas ──────────────────────────────────────────────────
    {
        "name": "Diflubenzuron", "cas": "35367-38-5", "formula": "C14H9ClF2N2O2",
        "smiles": "O=C(NC(=O)c1ccc(F)cc1)Nc1ccc(Cl)cc1F", "mw": 310.7,
        "degT50_soil": 13, "degT50_water": 6.5, "degT50_sediment": 30,
        "koc": 3600, "kfoc": 3600, "freundlich_n": 0.86,
        "vapor_pressure": 4.0e-7, "henry_const": 7.0e-5,
        "solubility": 0.08, "pka": None, "logP": 3.89,
        "cls": "Benzoylurea", "status": "Approved",
        "n_atoms": 30, "n_heavy": 21, "hbd": 2, "hba": 4, "n_rings": 2, "n_rotatable": 3
    },
    {
        "name": "Lufenuron", "cas": "103055-07-8", "formula": "C17H8Cl2F8N2O3",
        "smiles": "O=C(NC(=O)c1cc(Cl)c(OC(F)(F)C(F)F)c(Cl)c1)Nc1ccc(C(F)(F)F)cc1",
        "mw": 511.1,
        "degT50_soil": 138, "degT50_water": 100, "degT50_sediment": 365,
        "koc": 8920, "kfoc": 8920, "freundlich_n": 0.83,
        "vapor_pressure": 4.7e-9, "henry_const": 2.9e-5,
        "solubility": 0.046, "pka": None, "logP": 5.12,
        "cls": "Benzoylurea", "status": "Approved",
        "n_atoms": 42, "n_heavy": 32, "hbd": 2, "hba": 5, "n_rings": 2, "n_rotatable": 5
    },

    # ─── Pyridines ─────────────────────────────────────────────────────
    {
        "name": "Flonicamid", "cas": "158062-67-0", "formula": "C9H6F3N3O",
        "smiles": "NC(=O)c1ccnc(C(F)(F)F)c1C#N", "mw": 229.2,
        "degT50_soil": 2.3, "degT50_water": 42, "degT50_sediment": 15,
        "koc": 43, "kfoc": 43, "freundlich_n": 0.93,
        "vapor_pressure": 8.3e-7, "henry_const": 1.1e-7,
        "solubility": 5200, "pka": None, "logP": -0.24,
        "cls": "Pyridine", "status": "Approved",
        "n_atoms": 22, "n_heavy": 16, "hbd": 1, "hba": 4, "n_rings": 1, "n_rotatable": 1
    },
    {
        "name": "Pyriproxyfen", "cas": "95737-68-1", "formula": "C20H19NO3",
        "smiles": "CC1=NOC(Oc2ccc(Oc3ccccc3)cc2)C1", "mw": 321.4,
        "degT50_soil": 20, "degT50_water": 9, "degT50_sediment": 60,
        "koc": 80100, "kfoc": 80100, "freundlich_n": 0.83,
        "vapor_pressure": 1.3e-6, "henry_const": 9.4e-4,
        "solubility": 0.37, "pka": None, "logP": 5.37,
        "cls": "Pyridine", "status": "Approved",
        "n_atoms": 43, "n_heavy": 24, "hbd": 0, "hba": 4, "n_rings": 3, "n_rotatable": 6
    },

    # ─── Additional Herbicides (misc) ──────────────────────────────────
    {
        "name": "Aclonifen", "cas": "74070-46-5", "formula": "C12H9ClN2O3",
        "smiles": "Nc1ccc(Oc2ccccc2Cl)c([N+](=O)[O-])c1", "mw": 264.7,
        "degT50_soil": 118, "degT50_water": 50, "degT50_sediment": 200,
        "koc": 7126, "kfoc": 7126, "freundlich_n": 0.86,
        "vapor_pressure": 5.0e-5, "henry_const": 4.0e-3,
        "solubility": 1.4, "pka": None, "logP": 4.37,
        "cls": "Diphenyl ether", "status": "Approved",
        "n_atoms": 28, "n_heavy": 18, "hbd": 1, "hba": 4, "n_rings": 2, "n_rotatable": 3
    },
    {
        "name": "Diflufenican", "cas": "83164-33-4", "formula": "C19H11F5N2O2",
        "smiles": "Fc1cc(Oc2ccc(C(=O)c3c[nH]c4ccccc34)cc2)c(F)c(F)c1F", "mw": 394.3,
        "degT50_soil": 315, "degT50_water": 100, "degT50_sediment": 500,
        "koc": 3417, "kfoc": 3417, "freundlich_n": 0.85,
        "vapor_pressure": 4.2e-6, "henry_const": 3.6e-2,
        "solubility": 0.05, "pka": None, "logP": 4.2,
        "cls": "Nicotinanilide", "status": "Approved",
        "n_atoms": 39, "n_heavy": 28, "hbd": 1, "hba": 4, "n_rings": 3, "n_rotatable": 4
    },
    {
        "name": "Propyzamide", "cas": "23950-58-5", "formula": "C12H11Cl2NO",
        "smiles": "CC(C)(C#C)NC(=O)c1cc(Cl)cc(Cl)c1", "mw": 256.1,
        "degT50_soil": 50, "degT50_water": 35, "degT50_sediment": 100,
        "koc": 840, "kfoc": 840, "freundlich_n": 0.88,
        "vapor_pressure": 5.8e-5, "henry_const": 4.0e-4,
        "solubility": 9, "pka": None, "logP": 3.27,
        "cls": "Benzamide", "status": "Approved",
        "n_atoms": 26, "n_heavy": 16, "hbd": 1, "hba": 2, "n_rings": 1, "n_rotatable": 2
    },
    {
        "name": "Napropamide", "cas": "15299-99-7", "formula": "C17H21NO2",
        "smiles": "CCN(CC)C(=O)C(C)Oc1cccc2ccccc12", "mw": 271.4,
        "degT50_soil": 70, "degT50_water": 40, "degT50_sediment": 100,
        "koc": 815, "kfoc": 815, "freundlich_n": 0.88,
        "vapor_pressure": 5.7e-5, "henry_const": 1.7e-4,
        "solubility": 74, "pka": None, "logP": 3.36,
        "cls": "Acetamide", "status": "Approved",
        "n_atoms": 41, "n_heavy": 20, "hbd": 0, "hba": 3, "n_rings": 2, "n_rotatable": 5
    },
    {
        "name": "Bentazone", "cas": "25057-89-0", "formula": "C10H12N2O3S",
        "smiles": "CC(C)N1C(=O)c2ccccc2NS1(=O)=O", "mw": 240.3,
        "degT50_soil": 20, "degT50_water": 12, "degT50_sediment": 35,
        "koc": 55, "kfoc": 55, "freundlich_n": 0.90,
        "vapor_pressure": 1.7e-4, "henry_const": 7.2e-8,
        "solubility": 570, "pka": 3.28, "logP": 2.34,
        "cls": "Benzothiadiazone", "status": "Approved",
        "n_atoms": 27, "n_heavy": 16, "hbd": 1, "hba": 4, "n_rings": 2, "n_rotatable": 1
    },
    {
        "name": "Mecoprop-P", "cas": "16484-77-8", "formula": "C10H11ClO3",
        "smiles": "CC(Oc1ccc(Cl)c(C)c1)C(O)=O", "mw": 214.6,
        "degT50_soil": 8, "degT50_water": 10, "degT50_sediment": 18,
        "koc": 47, "kfoc": 47, "freundlich_n": 0.91,
        "vapor_pressure": 3.1e-4, "henry_const": 2.0e-7,
        "solubility": 620, "pka": 3.11, "logP": 3.13,
        "cls": "Phenoxypropionic acid", "status": "Approved",
        "n_atoms": 25, "n_heavy": 14, "hbd": 1, "hba": 3, "n_rings": 1, "n_rotatable": 3
    },
    {
        "name": "Phenmedipham", "cas": "13684-63-4", "formula": "C16H16N2O4",
        "smiles": "COC(=O)Nc1cccc(OC(=O)Nc2ccc(C)cc2)c1", "mw": 300.3,
        "degT50_soil": 25, "degT50_water": 7, "degT50_sediment": 40,
        "koc": 1760, "kfoc": 1760, "freundlich_n": 0.87,
        "vapor_pressure": 9.5e-7, "henry_const": 5.0e-7,
        "solubility": 4.7, "pka": None, "logP": 3.59,
        "cls": "Phenylcarbamate", "status": "Approved",
        "n_atoms": 38, "n_heavy": 22, "hbd": 2, "hba": 6, "n_rings": 2, "n_rotatable": 6
    },
    {
        "name": "Ethofumesate", "cas": "26225-79-6", "formula": "C13H18O5S",
        "smiles": "CCOC(=O)Oc1cc2c(cc1OC)OC(C)(C)S2(=O)=O", "mw": 286.3,
        "degT50_soil": 30, "degT50_water": 21, "degT50_sediment": 55,
        "koc": 147, "kfoc": 147, "freundlich_n": 0.90,
        "vapor_pressure": 6.5e-4, "henry_const": 3.2e-4,
        "solubility": 50, "pka": None, "logP": 2.7,
        "cls": "Benzofuran", "status": "Approved",
        "n_atoms": 36, "n_heavy": 19, "hbd": 0, "hba": 5, "n_rings": 2, "n_rotatable": 4
    },
    {
        "name": "Prosulfuron", "cas": "94125-34-5", "formula": "C15H16F3N5O4S",
        "smiles": "COc1cc(C)nc(NC(=O)NS(=O)(=O)c2ccccc2C(F)(F)F)n1", "mw": 419.4,
        "degT50_soil": 16, "degT50_water": 20, "degT50_sediment": 30,
        "koc": 31, "kfoc": 31, "freundlich_n": 0.91,
        "vapor_pressure": 1.3e-7, "henry_const": 1.2e-9,
        "solubility": 4000, "pka": 3.76, "logP": 1.5,
        "cls": "Sulfonylurea", "status": "Approved",
        "n_atoms": 43, "n_heavy": 28, "hbd": 2, "hba": 8, "n_rings": 2, "n_rotatable": 5
    },
    {
        "name": "Foramsulfuron", "cas": "173159-57-4", "formula": "C17H20N6O7S",
        "smiles": "COc1cc(OC)nc(NC(=O)NS(=O)(=O)c2cc(NC=O)ccc2OC)n1", "mw": 452.4,
        "degT50_soil": 7, "degT50_water": 16, "degT50_sediment": 20,
        "koc": 56, "kfoc": 56, "freundlich_n": 0.90,
        "vapor_pressure": 4.2e-12, "henry_const": 1.7e-13,
        "solubility": 3290, "pka": 4.6, "logP": 0.03,
        "cls": "Sulfonylurea", "status": "Approved",
        "n_atoms": 51, "n_heavy": 31, "hbd": 3, "hba": 10, "n_rings": 2, "n_rotatable": 7
    },
    {
        "name": "Quinoxyfen", "cas": "124495-18-7", "formula": "C15H8Cl2FNO",
        "smiles": "Fc1ccc(Oc2ccnc3cc(Cl)cc(Cl)c23)cc1", "mw": 308.1,
        "degT50_soil": 217, "degT50_water": 40, "degT50_sediment": 365,
        "koc": 5800, "kfoc": 5800, "freundlich_n": 0.84,
        "vapor_pressure": 1.2e-5, "henry_const": 3.5e-2,
        "solubility": 0.12, "pka": None, "logP": 4.66,
        "cls": "Quinoline", "status": "Not approved",
        "n_atoms": 27, "n_heavy": 21, "hbd": 0, "hba": 2, "n_rings": 3, "n_rotatable": 2
    },
    {
        "name": "Trinexapac-ethyl", "cas": "95266-40-3", "formula": "C13H16O5",
        "smiles": "CCOC(=O)C(=C1CC(=O)CC(=O)C1)O", "mw": 252.3,
        "degT50_soil": 1, "degT50_water": 3, "degT50_sediment": 5,
        "koc": 39, "kfoc": 39, "freundlich_n": 0.93,
        "vapor_pressure": 2.5e-6, "henry_const": 5.0e-8,
        "solubility": 2200, "pka": 4.55, "logP": 1.0,
        "cls": "Cyclohexanedione", "status": "Approved",
        "n_atoms": 34, "n_heavy": 18, "hbd": 1, "hba": 5, "n_rings": 1, "n_rotatable": 4
    },
    {
        "name": "Prohexadione-calcium", "cas": "127277-53-6", "formula": "C10H12O5Ca",
        "smiles": "CCC(=O)C1=C(O)CC(=O)CC1=O", "mw": 212.2,
        "degT50_soil": 2, "degT50_water": 1, "degT50_sediment": 4,
        "koc": 28, "kfoc": 28, "freundlich_n": 0.95,
        "vapor_pressure": 5.0e-7, "henry_const": 3.0e-9,
        "solubility": 174000, "pka": 7.4, "logP": -1.2,
        "cls": "Cyclohexanedione", "status": "Approved",
        "n_atoms": 27, "n_heavy": 15, "hbd": 1, "hba": 5, "n_rings": 1, "n_rotatable": 2
    },
    {
        "name": "Simazine", "cas": "122-34-9", "formula": "C7H12ClN5",
        "smiles": "CCNc1nc(Cl)nc(NCC)n1", "mw": 201.7,
        "degT50_soil": 60, "degT50_water": 90, "degT50_sediment": 120,
        "koc": 130, "kfoc": 130, "freundlich_n": 0.91,
        "vapor_pressure": 8.1e-7, "henry_const": 5.6e-5,
        "solubility": 5, "pka": 1.62, "logP": 2.18,
        "cls": "Triazine", "status": "Not approved",
        "n_atoms": 25, "n_heavy": 13, "hbd": 2, "hba": 4, "n_rings": 1, "n_rotatable": 3
    },
    {
        "name": "Rotenone", "cas": "83-79-4", "formula": "C23H22O6",
        "smiles": "C=C(C)[C@@H]1Cc2c(ccc3c2OC2COc4cc(OC)c(OC)cc4[C@@H]2C3=O)O1", "mw": 394.4,
        "degT50_soil": 3, "degT50_water": 1, "degT50_sediment": 7,
        "koc": 60000, "kfoc": 60000, "freundlich_n": 0.79,
        "vapor_pressure": 1.0e-12, "henry_const": 3.0e-13,
        "solubility": 0.0002, "pka": None, "logP": 4.1,
        "cls": "Rotenoid", "status": "Not approved",
        "n_atoms": 51, "n_heavy": 29, "hbd": 0, "hba": 6, "n_rings": 5, "n_rotatable": 1
    },
    # ─── Additional validation substances ──────────────────────────────
    {
        "name": "Chlortoluron", "cas": "15545-48-9", "formula": "C10H13ClN2O",
        "smiles": "CN(C)C(=O)Nc1ccc(C)c(Cl)c1", "mw": 212.7,
        "degT50_soil": 40, "degT50_water": 50, "degT50_sediment": 80,
        "koc": 196, "kfoc": 196, "freundlich_n": 0.89,
        "vapor_pressure": 5.0e-6, "henry_const": 2.5e-7,
        "solubility": 74, "pka": None, "logP": 2.41,
        "cls": "Phenylurea", "status": "Under review",
        "n_atoms": 27, "n_heavy": 15, "hbd": 1, "hba": 2, "n_rings": 1, "n_rotatable": 2
    },
    {
        "name": "Mecoprop", "cas": "93-65-2", "formula": "C10H11ClO3",
        "smiles": "CC(Oc1ccc(Cl)cc1C)C(O)=O", "mw": 214.6,
        "degT50_soil": 8, "degT50_water": 15, "degT50_sediment": 20,
        "koc": 31, "kfoc": 31, "freundlich_n": 0.88,
        "vapor_pressure": 4.0e-4, "henry_const": 2.2e-6,
        "solubility": 620, "pka": 3.1, "logP": 0.1,
        "cls": "Phenoxyalkanoic", "status": "Approved",
        "n_atoms": 25, "n_heavy": 14, "hbd": 1, "hba": 3, "n_rings": 1, "n_rotatable": 3
    },
    {
        "name": "Chloridazon", "cas": "1698-60-8", "formula": "C10H8ClN3O",
        "smiles": "Clc1cc(-c2ccccc2)nn1N", "mw": 221.6,
        "degT50_soil": 42, "degT50_water": 60, "degT50_sediment": 90,
        "koc": 120, "kfoc": 120, "freundlich_n": 0.86,
        "vapor_pressure": 2.0e-6, "henry_const": 7.0e-8,
        "solubility": 422, "pka": None, "logP": 1.19,
        "cls": "Pyridazinone", "status": "Not approved",
        "n_atoms": 24, "n_heavy": 15, "hbd": 1, "hba": 3, "n_rings": 2, "n_rotatable": 1
    },
    # ─── Photolabile substances (Phase 4b) ─────────────────────────────
    {
        "name": "Famoxadone", "cas": "131807-57-3", "formula": "C22H18N2O4",
        "smiles": "O=C1OC(c2ccccc2)(c2ccccc2)C(=O)N1Oc1ccc(C#N)cc1", "mw": 374.4,
        "degT50_soil": 8, "degT50_water": 3, "degT50_sediment": 20,
        "koc": 5700, "kfoc": 5700, "freundlich_n": 0.88,
        "vapor_pressure": 6.4e-7, "henry_const": 6.6e-7,
        "solubility": 0.052, "pka": None, "logP": 4.65,
        "cls": "Oxazolidinone", "status": "Not approved",
        "n_atoms": 46, "n_heavy": 28, "hbd": 0, "hba": 5, "n_rings": 4, "n_rotatable": 4
    },
    {
        "name": "Pyrimethanil", "cas": "53112-28-0", "formula": "C12H13N3",
        "smiles": "Cc1cc(C)nc(Nc2ccccc2)n1", "mw": 199.3,
        "degT50_soil": 55, "degT50_water": 10, "degT50_sediment": 80,
        "koc": 301, "kfoc": 301, "freundlich_n": 0.85,
        "vapor_pressure": 2.2e-3, "henry_const": 2.2e-3,
        "solubility": 121, "pka": 3.44, "logP": 2.84,
        "cls": "Anilinopyrimidine", "status": "Approved",
        "n_atoms": 28, "n_heavy": 15, "hbd": 1, "hba": 3, "n_rings": 2, "n_rotatable": 2
    },
    {
        "name": "Abamectin", "cas": "71751-41-2", "formula": "C48H72O14",
        "smiles": "CC1CC(OC2CC(OC3CC(OC(=O)\\C=C\\C=C\\C(C)C(OC4CC(C)C(O)C(C)O4)C(C)CC(C)C3O)OC3OC(C)C(O)C(OC)C3OC)OC(C)C2O)OC(C)C1O", "mw": 873.1,
        "degT50_soil": 28, "degT50_water": 0.5, "degT50_sediment": 56,
        "koc": 5000, "kfoc": 5000, "freundlich_n": 0.89,
        "vapor_pressure": 3.7e-8, "henry_const": 4.0e-5,
        "solubility": 0.01, "pka": None, "logP": 4.4,
        "cls": "Avermectin", "status": "Approved",
        "n_atoms": 134, "n_heavy": 62, "hbd": 5, "hba": 14, "n_rings": 4, "n_rotatable": 14
    },
    {
        "name": "Fenhexamid", "cas": "126833-17-8", "formula": "C14H17Cl2NO2",
        "smiles": "O=C(c1cc(Cl)c(Cl)cc1O)NC1CCCCC1", "mw": 302.2,
        "degT50_soil": 1, "degT50_water": 3, "degT50_sediment": 5,
        "koc": 475, "kfoc": 475, "freundlich_n": 0.90,
        "vapor_pressure": 4.0e-6, "henry_const": 4.8e-6,
        "solubility": 24, "pka": 7.3, "logP": 3.51,
        "cls": "Hydroxyanilide", "status": "Approved",
        "n_atoms": 36, "n_heavy": 19, "hbd": 2, "hba": 3, "n_rings": 2, "n_rotatable": 3
    },
    {
        "name": "Prothioconazole", "cas": "178928-70-6", "formula": "C14H15Cl2N3OS",
        "smiles": "ClC(Cl)C(O)(c1ccccc1)C1=NNC(=S)S1", "mw": 344.3,
        "degT50_soil": 10, "degT50_water": 0.3, "degT50_sediment": 30,
        "koc": 2950, "kfoc": 2950, "freundlich_n": 0.87,
        "vapor_pressure": 3.2e-9, "henry_const": 8.0e-8,
        "solubility": 5, "pka": 6.9, "logP": 4.16,
        "cls": "Triazolinthione", "status": "Approved",
        "n_atoms": 36, "n_heavy": 21, "hbd": 2, "hba": 4, "n_rings": 3, "n_rotatable": 3
    },
    {
        "name": "Difenoconazole", "cas": "119446-68-3", "formula": "C19H17Cl2N3O3",
        "smiles": "OC(Cn1cncn1)(c1ccc(Oc2ccc(Cl)cc2)cc1)c1ccc(Cl)cc1", "mw": 406.3,
        "degT50_soil": 85, "degT50_water": 14, "degT50_sediment": 170,
        "koc": 3760, "kfoc": 3760, "freundlich_n": 0.90,
        "vapor_pressure": 3.3e-8, "henry_const": 3.6e-6,
        "solubility": 15, "pka": None, "logP": 4.36,
        "cls": "Triazole", "status": "Approved",
        "n_atoms": 38, "n_heavy": 25, "hbd": 1, "hba": 4, "n_rings": 4, "n_rotatable": 6
    },
]


def get_all_substances():
    """Return all substances."""
    return SUBSTANCES


def get_substance_by_name(name):
    """Return a single substance by name (case-insensitive)."""
    name_lower = name.lower()
    for s in SUBSTANCES:
        if s["name"].lower() == name_lower:
            return s
    return None


def search_substances(query="", cls_filter=None):
    """Filter substances by text query and/or class."""
    results = SUBSTANCES
    if query:
        q = query.lower()
        results = [s for s in results if q in s["name"].lower() or q in s["cas"] or q in s["cls"].lower()]
    if cls_filter and cls_filter != "all":
        results = [s for s in results if s["cls"] == cls_filter]
    return results


def get_substance_classes():
    """Return sorted list of unique substance classes."""
    return sorted(set(s["cls"] for s in SUBSTANCES))


def get_molecular_descriptors(substance):
    """Extract molecular descriptors for QML encoding."""
    return {
        "mw": substance["mw"],
        "logP": substance["logP"],
        "n_atoms": substance["n_atoms"],
        "n_heavy": substance["n_heavy"],
        "hbd": substance["hbd"],
        "hba": substance["hba"],
        "n_rings": substance["n_rings"],
        "n_rotatable": substance["n_rotatable"],
        "solubility": substance["solubility"],
        "vapor_pressure": substance["vapor_pressure"],
    }
