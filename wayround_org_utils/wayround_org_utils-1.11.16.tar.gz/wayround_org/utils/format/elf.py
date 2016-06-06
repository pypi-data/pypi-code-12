
import copy
import mmap
import os.path
import logging

from wayround_org.utils.format.elf_enum import *

from wayround_org.utils.format.elf_bin import (
    read_e_ident,
    is_elf,
    e_ident_bitness,
    e_ident_endianness,
    e_ident_to_dict,

    read_elf_ehdr_x,
    read_elf_ehdr,

    elf32_ehdr_to_dict,
    elf64_ehdr_to_dict,
    elf_ehdr_to_dict,

    read_elf_shdr_x,
    read_elf_shdr,

    read_elf_phdr_x,
    read_elf_phdr,


    read_elf_section_header_table,
    read_elf_section_header_table_names,

    read_elf_program_header_table,

    read_dynamic_section,

    get_dynamic_libs_names,
    get_dynamic_runpath_values,
    convert_virtual_to_file
    )


def dict_byte_to_ints(elf_ehdr_dict, only_keys=None, endianness='little'):

    ret = copy.copy(elf_ehdr_dict)

    for i in ret.keys():
        work_it = False

        if isinstance(only_keys, (list, set)):
            if i in only_keys:
                work_it = True
        else:
            work_it = True

        if work_it:
            ret[i] = int.from_bytes(ret[i], endianness)

    return ret


def e_ident_text(e_ident_dict):

    ret = """\
Class:       {e_i_s_class}
Data:        {e_i_s_data}
Version:     {e_i_s_version}
OS ABI:      {e_i_s_osabi}
ABI Version: {e_i_s_abiversion}
""".format_map(e_ident_dict)

    return ret


def elf_x_ehdr_text(elf_ehdr_dict, endianness):

    ret = """\
Object file type                     0x{e_type:x}
Architecture                         0x{e_machine:x}
Object file version                  {e_version}
Entry point virtual address          0x{e_entry:08x}
Program header table file offset     0x{e_phoff:08x} ({e_phoff} B)
Section header table file offset     0x{e_shoff:08x} ({e_shoff} B)
Processor-specific flags             b{e_flags:b}
ELF header size in bytes             {e_ehsize} B
Program header table entry size      {e_phentsize} B
Program header table entry count     {e_phnum}
Section header table entry size      {e_shentsize} B
Section header table entry count     {e_shnum}
Section header string table index    {e_shstrndx}
""".format_map(dict_byte_to_ints(elf_ehdr_dict, endianness=endianness))

    return ret


def get_section_header_type_name(value):

    ret = None

    names = {
        SHT_NULL: 'NULL',
        SHT_PROGBITS: 'PROGBITS',
        SHT_SYMTAB: 'SYMTAB',
        SHT_STRTAB: 'STRTAB',
        SHT_RELA: 'RELA',
        SHT_HASH: 'HASH',
        SHT_DYNAMIC: 'DYNAMIC',
        SHT_NOTE: 'NOTE',
        SHT_NOBITS: 'NOBITS',
        SHT_REL: 'REL',
        SHT_SHLIB: 'SHLIB',
        SHT_DYNSYM: 'DYNSYM',
        SHT_INIT_ARRAY: 'INIT_ARRAY',
        SHT_FINI_ARRAY: 'FINI_ARRAY',
        SHT_PREINIT_ARRAY: 'PREINIT_ARRAY',
        SHT_GROUP: 'GROUP',
        SHT_SYMTAB_SHNDX: 'SYMTAB_SHNDX',
        SHT_NUM: 'NUM',
        SHT_LOOS: 'LOOS',
        SHT_GNU_ATTRIBUTES: 'GNU_ATTRIBUTES',
        SHT_GNU_HASH: 'GNU_HASH',
        SHT_GNU_LIBLIST: 'GNU_LIBLIST',
        SHT_CHECKSUM: 'CHECKSUM',
        SHT_LOSUNW: 'LOSUNW',
        SHT_SUNW_move: 'SUNW_move',
        SHT_SUNW_COMDAT: 'SUNW_COMDAT',
        SHT_SUNW_syminfo: 'SUNW_syminfo',
        SHT_GNU_verdef: 'GNU_verdef',
        SHT_GNU_verneed: 'GNU_verneed',
        SHT_GNU_versym: 'GNU_versym',
        SHT_HISUNW: 'HISUNW',
        SHT_HIOS: 'HIOS',
        SHT_LOPROC: 'LOPROC',
        SHT_HIPROC: 'HIPROC',
        SHT_LOUSER: 'LOUSER',
        SHT_HIUSER: 'HIUSER'
        }

    if value in names:
        ret = names[value]
    else:
        ret = '0x{:x}'.format(value)

    return ret


def get_program_header_type_name(value):

    ret = None

    names = {
        PT_NULL: 'NULL',
        PT_LOAD: 'LOAD',
        PT_DYNAMIC: 'DYNAMIC',
        PT_INTERP: 'INTERP',
        PT_NOTE: 'NOTE',
        PT_SHLIB: 'SHLIB',
        PT_PHDR: 'PHDR',
        PT_TLS: 'TLS',
        PT_NUM: 'NUM',
        PT_LOOS: 'LOOS',
        PT_GNU_EH_FRAME: 'GNU_EH_FRAME',
        PT_GNU_STACK: 'GNU_STACK',
        PT_GNU_RELRO: 'GNU_RELRO',
        PT_LOSUNW: 'LOSUNW',
        PT_SUNWBSS: 'SUNWBSS',
        PT_SUNWSTACK: 'SUNWSTACK',
        PT_HISUNW: 'HISUNW',
        PT_HIOS: 'HIOS',
        PT_LOPROC: 'LOPROC',
        PT_HIPROC: 'HIPROC'
        }

    if value in names:
        ret = names[value]
    else:
        ret = '0x{:x}'.format(value)

    return ret


def get_dynamic_type_name(value):
    ret = None

    names = {
        DT_NULL: 'DT_NULL',
        DT_NEEDED: 'DT_NEEDED',
        DT_PLTRELSZ: 'DT_PLTRELSZ',
        DT_PLTGOT: 'DT_PLTGOT',
        DT_HASH: 'DT_HASH',
        DT_STRTAB: 'DT_STRTAB',
        DT_SYMTAB: 'DT_SYMTAB',
        DT_RELA: 'DT_RELA',
        DT_RELASZ: 'DT_RELASZ',
        DT_RELAENT: 'DT_RELAENT',
        DT_STRSZ: 'DT_STRSZ',
        DT_SYMENT: 'DT_SYMENT',
        DT_INIT: 'DT_INIT',
        DT_FINI: 'DT_FINI',
        DT_SONAME: 'DT_SONAME',
        DT_RPATH: 'DT_RPATH',
        DT_SYMBOLIC: 'DT_SYMBOLIC',
        DT_REL: 'DT_REL',
        DT_RELSZ: 'DT_RELSZ',
        DT_RELENT: 'DT_RELENT',
        DT_PLTREL: 'DT_PLTREL',
        DT_DEBUG: 'DT_DEBUG',
        DT_TEXTREL: 'DT_TEXTREL',
        DT_JMPREL: 'DT_JMPREL',
        DT_BIND_NOW: 'DT_BIND_NOW',
        DT_INIT_ARRAY: 'DT_INIT_ARRAY',
        DT_FINI_ARRAY: 'DT_FINI_ARRAY',
        DT_INIT_ARRAYSZ: 'DT_INIT_ARRAYSZ',
        DT_FINI_ARRAYSZ: 'DT_FINI_ARRAYSZ',
        DT_RUNPATH: 'DT_RUNPATH',
        DT_FLAGS: 'DT_FLAGS',
        DT_ENCODING: 'DT_ENCODING',
        DT_PREINIT_ARRAY: 'DT_PREINIT_ARRAY',
        DT_PREINIT_ARRAYSZ: 'DT_PREINIT_ARRAYSZ',
        DT_NUM: 'DT_NUM',
        DT_LOOS: 'DT_LOOS',
        DT_HIOS: 'DT_HIOS',
        DT_LOPROC: 'DT_LOPROC',
        DT_HIPROC: 'DT_HIPROC',
        DT_PROCNUM: 'DT_PROCNUM',
        DT_VALRNGLO: 'DT_VALRNGLO',
        DT_GNU_PRELINKED: 'DT_GNU_PRELINKED',
        DT_GNU_CONFLICTSZ: 'DT_GNU_CONFLICTSZ',
        DT_GNU_LIBLISTSZ: 'DT_GNU_LIBLISTSZ',
        DT_CHECKSUM: 'DT_CHECKSUM',
        DT_PLTPADSZ: 'DT_PLTPADSZ',
        DT_MOVEENT: 'DT_MOVEENT',
        DT_MOVESZ: 'DT_MOVESZ',
        DT_FEATURE_1: 'DT_FEATURE_1',
        DT_POSFLAG_1: 'DT_POSFLAG_1',
        DT_SYMINSZ: 'DT_SYMINSZ',
        DT_SYMINENT: 'DT_SYMINENT',
        DT_VALRNGHI: 'DT_VALRNGHI',
        DT_VALNUM: 'DT_VALNUM',
        DT_ADDRRNGLO: 'DT_ADDRRNGLO',
        DT_GNU_HASH: 'DT_GNU_HASH',
        DT_TLSDESC_PLT: 'DT_TLSDESC_PLT',
        DT_TLSDESC_GOT: 'DT_TLSDESC_GOT',
        DT_GNU_CONFLICT: 'DT_GNU_CONFLICT',
        DT_GNU_LIBLIST: 'DT_GNU_LIBLIST',
        DT_CONFIG: 'DT_CONFIG',
        DT_DEPAUDIT: 'DT_DEPAUDIT',
        DT_AUDIT: 'DT_AUDIT',
        DT_PLTPAD: 'DT_PLTPAD',
        DT_MOVETAB: 'DT_MOVETAB',
        DT_SYMINFO: 'DT_SYMINFO',
        DT_ADDRRNGHI: 'DT_ADDRRNGHI',
        DT_ADDRNUM: 'DT_ADDRNUM',
        DT_VERSYM: 'DT_VERSYM',
        DT_RELACOUNT: 'DT_RELACOUNT',
        DT_RELCOUNT: 'DT_RELCOUNT',
        DT_FLAGS_1: 'DT_FLAGS_1',
        DT_VERDEF: 'DT_VERDEF',
        DT_VERDEFNUM: 'DT_VERDEFNUM',
        DT_VERNEED: 'DT_VERNEED',
        DT_VERNEEDNUM: 'DT_VERNEEDNUM',
        DT_VERSIONTAGNUM: 'DT_VERSIONTAGNUM',
        DT_AUXILIARY: 'DT_AUXILIARY',
        DT_FILTER: 'DT_FILTER',
        DT_EXTRANUM: 'DT_EXTRANUM',
        }

    if value in names:
        ret = names[value]
    else:
        ret = '0x{:x}'.format(value)

    return ret

MACHINE_DICT = {
    EM_NONE: {
        'name': 'EM_NONE',
        'descr': 'No machine'
    },
    EM_M32: {
        'name': 'EM_M32',
        'descr': 'AT&T WE 32100'
    },
    EM_SPARC: {
        'name': 'EM_SPARC',
        'descr': 'SUN SPARC'
    },
    EM_386: {
        'name': 'EM_386',
        'descr': 'Intel 80386'
    },
    EM_68K: {
        'name': 'EM_68K',
        'descr': 'Motorola m68k family'
    },
    EM_88K: {
        'name': 'EM_88K',
        'descr': 'Motorola m88k family'
    },
    EM_860: {
        'name': 'EM_860',
        'descr': 'Intel 80860'
    },
    EM_MIPS: {
        'name': 'EM_MIPS',
        'descr': 'MIPS R3000 big-endian'
    },
    EM_S370: {
        'name': 'EM_S370',
        'descr': 'IBM System/370'
    },
    EM_MIPS_RS3_LE: {
        'name': 'EM_MIPS_RS3_LE',
        'descr': 'MIPS R3000 little-endian'
    },
    EM_PARISC: {
        'name': 'EM_PARISC',
        'descr': 'HPPA'
    },
    EM_VPP500: {
        'name': 'EM_VPP500',
        'descr': 'Fujitsu VPP500'
    },
    EM_SPARC32PLUS: {
        'name': 'EM_SPARC32PLUS',
        'descr': 'Sun\'s "v8plus"'
    },
    EM_960: {
        'name': 'EM_960',
        'descr': 'Intel 80960'
    },
    EM_PPC: {
        'name': 'EM_PPC',
        'descr': 'PowerPC'
    },
    EM_PPC64: {
        'name': 'EM_PPC64',
        'descr': 'PowerPC 64-bit'
    },
    EM_S390: {
        'name': 'EM_S390',
        'descr': 'IBM S390'
    },
    EM_V800: {
        'name': 'EM_V800',
        'descr': 'NEC V800 series'
    },
    EM_FR20: {
        'name': 'EM_FR20',
        'descr': 'Fujitsu FR20'
    },
    EM_RH32: {
        'name': 'EM_RH32',
        'descr': 'TRW RH-32'
    },
    EM_RCE: {
        'name': 'EM_RCE',
        'descr': 'Motorola RCE'
    },
    EM_ARM: {
        'name': 'EM_ARM',
        'descr': 'ARM'
    },
    EM_FAKE_ALPHA: {
        'name': 'EM_FAKE_ALPHA',
        'descr': 'Digital Alpha'
    },
    EM_SH: {
        'name': 'EM_SH',
        'descr': 'Hitachi SH'
    },
    EM_SPARCV9: {
        'name': 'EM_SPARCV9',
        'descr': 'SPARC v9 64-bit'
    },
    EM_TRICORE: {
        'name': 'EM_TRICORE',
        'descr': 'Siemens Tricore'
    },
    EM_ARC: {
        'name': 'EM_ARC',
        'descr': 'Argonaut RISC Core'
    },
    EM_H8_300: {
        'name': 'EM_H8_300',
        'descr': 'Hitachi H8/300'
    },
    EM_H8_300H: {
        'name': 'EM_H8_300H',
        'descr': 'Hitachi H8/300H'
    },
    EM_H8S: {
        'name': 'EM_H8S',
        'descr': 'Hitachi H8S'
    },
    EM_H8_500: {
        'name': 'EM_H8_500',
        'descr': 'Hitachi H8/500'
    },
    EM_IA_64: {
        'name': 'EM_IA_64',
        'descr': 'Intel Merced'
    },
    EM_MIPS_X: {
        'name': 'EM_MIPS_X',
        'descr': 'Stanford MIPS-X'
    },
    EM_COLDFIRE: {
        'name': 'EM_COLDFIRE',
        'descr': 'Motorola Coldfire'
    },
    EM_68HC12: {
        'name': 'EM_68HC12',
        'descr': 'Motorola M68HC12'
    },
    EM_MMA: {
        'name': 'EM_MMA',
        'descr': 'Fujitsu MMA Multimedia Accelerator'
    },
    EM_PCP: {
        'name': 'EM_PCP',
        'descr': 'Siemens PCP'
    },
    EM_NCPU: {
        'name': 'EM_NCPU',
        'descr': 'Sony nCPU embeeded RISC'
    },
    EM_NDR1: {
        'name': 'EM_NDR1',
        'descr': 'Denso NDR1 microprocessor'
    },
    EM_STARCORE: {
        'name': 'EM_STARCORE',
        'descr': 'Motorola Start*Core processor'
    },
    EM_ME16: {
        'name': 'EM_ME16',
        'descr': 'Toyota ME16 processor'
    },
    EM_ST100: {
        'name': 'EM_ST100',
        'descr': 'STMicroelectronic ST100 processor'
    },
    EM_TINYJ: {
        'name': 'EM_TINYJ',
        'descr': 'Advanced Logic Corp. Tinyj emb.fam'
    },
    EM_X86_64: {
        'name': 'EM_X86_64',
        'descr': 'AMD x86-64 architecture'
    },
    EM_PDSP: {
        'name': 'EM_PDSP',
        'descr': 'Sony DSP Processor'
    },
    EM_FX66: {
        'name': 'EM_FX66',
        'descr': 'Siemens FX66 microcontroller'
    },
    EM_ST9PLUS: {
        'name': 'EM_ST9PLUS',
        'descr': 'STMicroelectronics ST9+ 8/16 mc'
    },
    EM_ST7: {
        'name': 'EM_ST7',
        'descr': 'STmicroelectronics ST7 8 bit mc'
    },
    EM_68HC16: {
        'name': 'EM_68HC16',
        'descr': 'Motorola MC68HC16 microcontroller'
    },
    EM_68HC11: {
        'name': 'EM_68HC11',
        'descr': 'Motorola MC68HC11 microcontroller'
    },
    EM_68HC08: {
        'name': 'EM_68HC08',
        'descr': 'Motorola MC68HC08 microcontroller'
    },
    EM_68HC05: {
        'name': 'EM_68HC05',
        'descr': 'Motorola MC68HC05 microcontroller'
    },
    EM_SVX: {
        'name': 'EM_SVX',
        'descr': 'Silicon Graphics SVx'
    },
    EM_ST19: {
        'name': 'EM_ST19',
        'descr': 'STMicroelectronics ST19 8 bit mc'
    },
    EM_VAX: {
        'name': 'EM_VAX',
        'descr': 'Digital VAX'
    },
    EM_CRIS: {
        'name': 'EM_CRIS',
        'descr': 'Axis Communications 32-bit embedded processor'
    },
    EM_JAVELIN: {
        'name': 'EM_JAVELIN',
        'descr': 'Infineon Technologies 32-bit embedded processor'
    },
    EM_FIREPATH: {
        'name': 'EM_FIREPATH',
        'descr': 'Element 14 64-bit DSP Processor'
    },
    EM_ZSP: {
        'name': 'EM_ZSP',
        'descr': 'LSI Logic 16-bit DSP Processor'
    },
    EM_MMIX: {
        'name': 'EM_MMIX',
        'descr': 'Donald Knuth\'s educational 64 - bit processor'
    },
    EM_HUANY: {
        'name': 'EM_HUANY',
        'descr': 'Harvard University machine-independent object files'
    },
    EM_PRISM: {
        'name': 'EM_PRISM',
        'descr': 'SiTera Prism'
    },
    EM_AVR: {
        'name': 'EM_AVR',
        'descr': 'Atmel AVR 8-bit microcontroller'
    },
    EM_FR30: {
        'name': 'EM_FR30',
        'descr': 'Fujitsu FR30'
    },
    EM_D10V: {
        'name': 'EM_D10V',
        'descr': 'Mitsubishi D10V'
    },
    EM_D30V: {
        'name': 'EM_D30V',
        'descr': 'Mitsubishi D30V'
    },
    EM_V850: {
        'name': 'EM_V850',
        'descr': 'NEC v850'
    },
    EM_M32R: {
        'name': 'EM_M32R',
        'descr': 'Mitsubishi M32R'
    },
    EM_MN10300: {
        'name': 'EM_MN10300',
        'descr': 'Matsushita MN10300'
    },
    EM_MN10200: {
        'name': 'EM_MN10200',
        'descr': 'Matsushita MN10200'
    },
    EM_PJ: {
        'name': 'EM_PJ',
        'descr': 'picoJava'
    },
    EM_OPENRISC: {
        'name': 'EM_OPENRISC',
        'descr': 'OpenRISC 32-bit embedded processor'
    },
    EM_ARC_A5: {
        'name': 'EM_ARC_A5',
        'descr': 'ARC Cores Tangent-A5'
    },
    EM_XTENSA: {
        'name': 'EM_XTENSA',
        'descr': 'Tensilica Xtensa Architecture'
    },
    EM_TILEPRO: {
        'name': 'EM_TILEPRO',
        'descr': 'Tilera TILEPro'
    },
    EM_TILEGX: {
        'name': 'EM_TILEGX',
        'descr': 'Tilera TILE-Gx'
    },
    EM_NUM: {
        'name': 'EM_NUM',
        'descr': ''
    },
    EM_ALPHA: {
        'name': 'EM_ALPHA',
        'descr': ''
    }
}


def machine_name_by_int(value):
    return MACHINE_DICT[value]['name']


def machine_descr_by_int(value):
    return MACHINE_DICT[value]['descr']


def machine_int_by_name(name):
    ret = None
    for i, j in MACHINE_DICT:
        if j['name'] == name:
            ret = i
            break
    return ret


def section_header_table_text(
        data,
        elf_section_header_table,
        ehdr_dict,
        endianness,
        bitness
        ):

    ret = ''

    names = read_elf_section_header_table_names(
        data, elf_section_header_table, ehdr_dict, endianness
        )

    section_header_table2 = []
    for i in elf_section_header_table:
        section_header_table2.append(
            dict_byte_to_ints(
                i,
                endianness=endianness
                )
            )

    elf_section_header_table = section_header_table2

    longest = 0
    for i in names:
        if len(i) > longest:
            longest = len(i)

    types = []
    for i in range(len(elf_section_header_table)):
        types.append(
            get_section_header_type_name(
                elf_section_header_table[i]['sh_type'])
            )

    longest_t = 0
    for i in types:
        if len(i) > longest_t:
            longest_t = len(i)

    if bitness == 32:

        ret += "  [{index:2}] "\
            "{name}(sto:{name_addr:5}) "\
            "{typ} "\
            "{addr:8} "\
            "{off:8} "\
            "{size:8} "\
            "{es:2} "\
            "{flg:10} "\
            "{lk:3} "\
            "{inf:3} "\
            "{al:3}\n".format(
                index='No',
                name='Name'.ljust(longest),
                name_addr='',
                typ='Type'.ljust(longest_t),
                flg='Flags',
                addr='Address',
                off='Offset',
                size='Size',
                lk='Lnk',
                inf='Inf',
                al='Al',
                es='SZ'
            )

        for i in range(len(elf_section_header_table)):
            ret += "  [{index:2}] "\
                "{name}(sto:{name_addr:5x}) "\
                "{typ} "\
                "{addr:08x} "\
                "{off:08x} "\
                "{size:08x} "\
                "{es:02x} "\
                "{flg:010b} "\
                "{lk:03x} "\
                "{inf:03x} "\
                "{al:03x}\n".format(
                    index=i,
                    name=names[i].ljust(longest),
                    name_addr=elf_section_header_table[i]['sh_name'],
                    typ=types[i].ljust(longest_t),
                    flg=elf_section_header_table[i]['sh_flags'],
                    addr=elf_section_header_table[i]['sh_addr'],
                    off=elf_section_header_table[i]['sh_offset'],
                    size=elf_section_header_table[i]['sh_size'],
                    lk=elf_section_header_table[i]['sh_link'],
                    inf=elf_section_header_table[i]['sh_info'],
                    al=elf_section_header_table[i]['sh_addralign'],
                    es=elf_section_header_table[i]['sh_entsize']
                )

    elif bitness == 64:

        ret += "  [{index:2}] "\
            "{name}(sto:{name_addr:5}) "\
            "{typ} "\
            "{addr:16} "\
            "{off:16} "\
            "{size:16} "\
            "{es:2} "\
            "{flg:10} "\
            "{lk:3} "\
            "{inf:3} "\
            "{al:3}\n".format(
                index='No',
                name='Name'.ljust(longest),
                name_addr='',
                typ='Type'.ljust(longest_t),
                flg='Flags',
                addr='Address',
                off='Offset',
                size='Size',
                lk='Lnk',
                inf='Inf',
                al='Al',
                es='SZ'
            )

        for i in range(len(elf_section_header_table)):
            ret += "  [{index:2}] "\
                "{name}(sto:{name_addr:5x}) "\
                "{typ} "\
                "{addr:016x} "\
                "{off:016x} "\
                "{size:016x} "\
                "{es:02x} "\
                "{flg:010b} "\
                "{lk:03x} "\
                "{inf:03x} "\
                "{al:03x}\n".format(
                    index=i,
                    name=names[i].ljust(longest),
                    name_addr=elf_section_header_table[i]['sh_name'],
                    typ=types[i].ljust(longest_t),
                    flg=elf_section_header_table[i]['sh_flags'],
                    addr=elf_section_header_table[i]['sh_addr'],
                    off=elf_section_header_table[i]['sh_offset'],
                    size=elf_section_header_table[i]['sh_size'],
                    lk=elf_section_header_table[i]['sh_link'],
                    inf=elf_section_header_table[i]['sh_info'],
                    al=elf_section_header_table[i]['sh_addralign'],
                    es=elf_section_header_table[i]['sh_entsize']
                )

    else:
        raise Exception("unknown bitness: {}".format(bitness))

    ret += '\n'
    ret += 'sto - string table offset\n'

    return ret


def program_header_table_text(program_header_table, endianness, bitness=32):

    ret = ''

    program_header_table2 = []
    for i in program_header_table:
        program_header_table2.append(
            dict_byte_to_ints(
                i,
                endianness=endianness
                )
            )

    program_header_table = program_header_table2

    types = []
    for i in range(len(program_header_table)):
        types.append(
            get_program_header_type_name(
                program_header_table[i]['p_type']))

    longest_t = 0
    for i in types:
        if len(i) > longest_t:
            longest_t = len(i)

    if bitness == 32:

        ret += "  {typ} "\
            "{offset:8} "\
            "{virtaddr:8} "\
            "{physaddr:8} "\
            "{filesize:8} "\
            "{memsize:8} "\
            "{flag:10} "\
            "{align:8}\n".format(
                typ='Type'.ljust(longest_t),
                flag='Flags',
                offset='F Offset',
                virtaddr='VirtAddr',
                physaddr='PhisAddr',
                filesize='FileSize',
                memsize='MemSize',
                align='Align'
            )

        for i in range(len(program_header_table)):
            ret += "  {typ} "\
                "{offset:08x} "\
                "{virtaddr:08x} "\
                "{physaddr:08x} "\
                "{filesize:08x} "\
                "{memsize:08x} "\
                "{flag:010b} "\
                "{align:08x}\n".format(
                    typ=types[i].ljust(longest_t),
                    flag=program_header_table[i]['p_flags'],
                    offset=program_header_table[i]['p_offset'],
                    virtaddr=program_header_table[i]['p_vaddr'],
                    physaddr=program_header_table[i]['p_paddr'],
                    filesize=program_header_table[i]['p_filesz'],
                    memsize=program_header_table[i]['p_memsz'],
                    align=program_header_table[i]['p_align']
                )

    elif bitness == 64:

        ret += "  {typ} "\
            "{offset:16} "\
            "{virtaddr:16} "\
            "{physaddr:16} "\
            "{filesize:16} "\
            "{memsize:16} "\
            "{flag:10} "\
            "{align:16}\n".format(
                typ='Type'.ljust(longest_t),
                flag='Flags',
                offset='F Offset',
                virtaddr='VirtAddr',
                physaddr='PhisAddr',
                filesize='FileSize',
                memsize='MemSize',
                align='Align'
            )

        for i in range(len(program_header_table)):
            ret += "  {typ} "\
                "{offset:016x} "\
                "{virtaddr:016x} "\
                "{physaddr:016x} "\
                "{filesize:016x} "\
                "{memsize:016x} "\
                "{flag:010b} "\
                "{align:016x}\n".format(
                    typ=types[i].ljust(longest_t),
                    flag=program_header_table[i]['p_flags'],
                    offset=program_header_table[i]['p_offset'],
                    virtaddr=program_header_table[i]['p_vaddr'],
                    physaddr=program_header_table[i]['p_paddr'],
                    filesize=program_header_table[i]['p_filesz'],
                    memsize=program_header_table[i]['p_memsz'],
                    align=program_header_table[i]['p_align']
                )

    else:
        raise Exception("unknown bitness: {}".format(bitness))

    return ret


def dynamic_section_text(dinamics_table, endianness):

    ret = ''

    names = []

    for i in range(len(dinamics_table)):
        names.append(get_dynamic_type_name(dinamics_table[i]['d_tag']))

    longest_t = 0
    for i in names:
        if len(i) > longest_t:
            longest_t = len(i)

    for i in dinamics_table:
        number = 0
        if get_dynamic_type_name(i['d_tag']) == 'DT_NEEDED':
            number = i['d_ptr']
        else:
            number = i['d_val']
        ret += "{}  {:08x}\n".format(
            get_dynamic_type_name(i['d_tag']).ljust(longest_t),
            number
            )

    return ret


class ELF:

    def __init__(self, filename, verbose=False, debug=False, mute=False):

        error = False

        self.debug = debug

        self.verbose = verbose

        self.mute = mute

        _FILLABLE_ATTRIBUTE_NAMES = [
            'e_ident',
            'bitness',
            'endianness',
            'e_ident_dict',
            'e_ident_text',
            'elf_ehdr',
            'elf_ehdr_dict',
            'elf_x_ehdr_text',

            'elf_type',
            'elf_type_name',

            'elf_machine',
            'elf_machine_name',
            'elf_machine_descr',

            'section_table',
            'section_names',
            'program_table',
            'section_header_table_text',
            'program_header_table_text',
            'dynamic_section_index',
            'dynamic_section_offset',
            'dynamic_section',
            'dynamic_section_text',
            'needed_libs_list',
            'runpath_values',
            'libs_list_text'
            ]

        if debug or verbose:
            print("File `{}'".format(filename))

        self.opened = False

        self.filename = filename

        if not os.path.isfile(filename):
            if not mute:
                logging.error("Not a file: `{}'".format(filename))
                error = True

        if not error:

            if os.stat(filename).st_size == 0:
                if not mute and verbose:
                    logging.info("File size is 0: {}".format(filename))
                error = True

        f = None
        m = None

        if not error:

            try:
                f = open(filename, 'rb')
            except KeyboardInterrupt:
                error = True
                raise
            except:
                if not mute:
                    logging.exception(
                        "Couldn't open file for read: `{}'".format(
                            filename)
                        )
                error = True

        if not error:

            try:
                m = mmap.mmap(
                    f.fileno(),
                    0,
                    flags=mmap.MAP_PRIVATE,
                    prot=mmap.PROT_READ
                    )
            except KeyboardInterrupt:
                raise
                error = True
            except:
                if not mute:
                    logging.exception(
                        "Couldn't map file: `{}'".format(filename)
                        )
                error = True

        if not error:

            self.opened = True

            self.is_elf = self._fill_is_elf(m, debug)

            errors = 0

            for i in _FILLABLE_ATTRIBUTE_NAMES:

                setattr(self, i, None)

                if self.is_elf:

                    filler = getattr(
                        self,
                        '_fill_{}'.format(i)
                        )

                    filler_res = filler(m, debug)

                    setattr(self, i, filler_res)

                else:
                    # NOTE: not an error. but attributes must
                    #       be set atleast to None, so not a break
                    pass

            if errors != 0:
                error = True

        if m:
            m.close()

        if f:
            f.close()

        self.error = error

        if error:
            self.is_elf = False
            for i in _FILLABLE_ATTRIBUTE_NAMES:
                setattr(self, i, None)

        return

    def return_text(self):
        ret = """\
file: {filename}

is elf?: {is_elf}

({bitness}-bit)
({endianness}-byteorder)

{e_ident_text}

{elf_x_ehdr_text}

Section table:
{section_header_table_text}

Program table:
{program_header_table_text}

Dynamic section:
{dynamic_section_text}

Needed libs list:
{libs_list_text}
""".format(
            filename=self.filename,
            is_elf=self.is_elf,
            bitness=self.bitness,
            endianness=self.endianness,
            e_ident_text=self.e_ident_text,
            elf_x_ehdr_text=self.elf_x_ehdr_text,
            section_header_table_text=self.section_header_table_text,
            program_header_table_text=self.program_header_table_text,
            dynamic_section_text=self.dynamic_section_text,
            libs_list_text=self.libs_list_text
            )

        return ret

    def _fill_is_elf(self, m, debug):
        return is_elf(m)

    def _fill_e_ident(self, m, debug):

        ret = read_e_ident(m)
        if debug:
            print("e_ident == {}".format(ret))

        return ret

    def _fill_bitness(self, m, debug):
        ret = None

        if self.e_ident:
            ret = e_ident_bitness(self.e_ident)

        if debug:
            print("bitness == {}".format(ret))

        return ret

    def _fill_endianness(self, m, debug):

        ret = None
        if self.e_ident:
            ret = e_ident_endianness(self.e_ident)

        if debug:
            print("endianness == {}".format(ret))

        return ret

    def _fill_elf_machine(self, m, debug):

        ret = None
        if self.elf_ehdr_dict and self.endianness:

            ret = int.from_bytes(
                self.elf_ehdr_dict['e_machine'],
                self.endianness
                )

        if debug:
            print("elf_machine == {}".format(ret))

        return ret

    def _fill_elf_machine_name(self, m, debug):
        ret = None

        if self.elf_machine:
            ret = machine_name_by_int(self.elf_machine)

        if debug:
            print("elf_machine_name == {}".format(ret))

        return ret

    def _fill_elf_machine_descr(self, m, debug):

        ret = None

        if self.elf_machine:

            ret = machine_descr_by_int(self.elf_machine)

        if debug:
            print("elf_machine_descr == {}".format(ret))

        return ret

    def _fill_elf_type(self, m, debug):
        ret = None
        if self.elf_ehdr_dict and self.endianness:

            ret = int.from_bytes(
                self.elf_ehdr_dict['e_type'],
                self.endianness
                )

        if debug:
            print("elf_type == {}".format(ret))

        return ret

    def _fill_elf_type_name(self, m, debug):

        ret = 0

        if self.elf_type:

            for i in [
                    'ET_NONE',
                    'ET_REL',
                    'ET_EXEC',
                    'ET_DYN',
                    'ET_CORE',
                    'ET_NUM',
                    'ET_LOOS',
                    'ET_HIOS',
                    'ET_LOPROC',
                    'ET_HIPROC'
                    ]:

                if self.elf_type == eval(i):
                    ret = i
                    break

        if debug:
            print("elf_type_name == {}".format(ret))
        return ret

    def _fill_e_ident_dict(self, m, debug):

        ret = None

        if self.e_ident:
            ret = e_ident_to_dict(self.e_ident)

        if debug:
            print("e_ident_dict == {}".format(ret))

        return ret

    def _fill_e_ident_text(self, m, debug):

        ret = 0

        if self.e_ident_dict:

            ret = e_ident_text(self.e_ident_dict)

        if debug:
            print("e_ident_text == {}".format(ret))

        return ret

    def _fill_elf_ehdr(self, m, debug):

        ret = None

        if self.e_ident_dict:
            ret = read_elf_ehdr(
                m,
                0,
                self.e_ident_dict
                )

        if debug:
            print("elf_ehdr == {}".format(ret))

        return ret

    def _fill_elf_ehdr_dict(self, m, debug):

        ret = None

        if self.e_ident_dict:
            ret = elf_ehdr_to_dict(
                m,
                0,
                self.e_ident_dict
                )

        if debug:
            print("elf_ehdr_dict == {}".format(ret))

        return ret

    def _fill_elf_x_ehdr_text(self, m, debug):

        ret = None

        if self.elf_ehdr_dict and self.endianness:

            ret = elf_x_ehdr_text(
                self.elf_ehdr_dict,
                self.endianness
                )

        if debug:
            print("elf_x_ehdr_text == {}".format(ret))

        return ret

    def _fill_section_table(self, m, debug):

        ret = None

        if self.e_ident_dict and self.elf_ehdr_dict:

            ret = read_elf_section_header_table(
                m,
                self.e_ident_dict,
                self.elf_ehdr_dict
                )

        if debug:
            print("section_table == {}".format(ret))

        return ret

    def _fill_section_names(self, m, debug):

        ret = None

        if (self.section_table
                and self.elf_ehdr_dict
                and self.endianness):

            ret = read_elf_section_header_table_names(
                m,
                self.section_table,
                self.elf_ehdr_dict,
                self.endianness
                )

        if debug:
            print("section_names == {}".format(ret))

        return ret

    def _fill_program_table(self, m, debug):

        ret = None
        if self.e_ident_dict and self.elf_ehdr_dict:
            ret = read_elf_program_header_table(
                m,
                self.e_ident_dict,
                self.elf_ehdr_dict
                )

        if debug:
            print("program_table == {}".format(ret))

        return ret

    def _fill_section_header_table_text(self, m, debug):

        ret = None
        if (self.section_table
                and self.elf_ehdr_dict
                and self.endianness):

            ret = (
                section_header_table_text(
                    m,
                    self.section_table,
                    self.elf_ehdr_dict,
                    self.endianness,
                    self.bitness
                    )
                )

        if debug:
            print("section_header_table_text == {}".format(ret))

        return ret

    def _fill_program_header_table_text(self, m, debug):

        ret = None
        if self.program_table and self.endianness:

            ret = program_header_table_text(
                self.program_table,
                self.endianness,
                self.bitness
                )

        if debug:
            print("program_header_table_text == {}".format(ret))

        return ret

    def _fill_dynamic_section_index(self, m, debug):

        ret = None
        if (
                self.section_names
                and '.dynamic' in self.section_names
                and self.section_table
                and int.from_bytes(
                    self.section_table[
                        self.section_names.index('.dynamic')
                        ]['sh_type'],
                    self.endianness,
                    signed=False
                    ) == SHT_DYNAMIC
                ):

            ret = self.section_names.index('.dynamic')

        if debug:
            print("dynamic_section_index == {}".format(ret))

        return ret

    def _fill_dynamic_section_offset(self, m, debug):

        ret = None
        if (self.section_table
            and self.dynamic_section_index
            and self.endianness
            and 'sh_offset' in self.section_table[
                        self.dynamic_section_index
                        ]
            ):

            ret = int.from_bytes(
                self.section_table[self.dynamic_section_index]['sh_offset'],
                self.endianness
                )

        if debug:
            print("dynamic_section_offset == {}".format(ret))

        return ret

    def _fill_dynamic_section(self, m, debug):

        ret = None
        if self.dynamic_section_offset and self.bitness and self.endianness:
            ret = read_dynamic_section(
                m,
                self.dynamic_section_offset,
                self.bitness,
                self.endianness
                )

        if debug:
            print("dynamic_section == {}".format(ret))

        return ret

    def _fill_dynamic_section_text(self, m, debug):

        ret = None
        if self.dynamic_section and self.endianness:
            ret = dynamic_section_text(
                self.dynamic_section,
                self.endianness
                )

        if debug:
            print("dynamic_section_text == {}".format(ret))
        return ret

    def _fill_needed_libs_list(self, m, debug):

        ret = None
        if (self.program_table
                and self.dynamic_section
                and self.section_table
                and self.endianness):

            ret = get_dynamic_libs_names(
                m,
                self.program_table,
                self.dynamic_section,
                self.section_table,
                self.endianness
                )

        if debug:
            print("needed_libs_list == {}".format(ret))

        return ret

    def _fill_runpath_values(self, m, debug):

        ret = None
        if (self.program_table
                and self.dynamic_section
                and self.section_table
                and self.endianness):

            ret = get_dynamic_runpath_values(
                m,
                self.program_table,
                self.dynamic_section,
                self.section_table,
                self.endianness
                )

        if debug:
            print("runpath_values == {}".format(ret))

        return ret

    def _fill_libs_list_text(self, m, debug):
        ret = None

        if self.needed_libs_list:
            ret = "{}.".format(', '.join(self.needed_libs_list))

        if debug:
            print("libs_list_text == {}".format(ret))

        return ret
