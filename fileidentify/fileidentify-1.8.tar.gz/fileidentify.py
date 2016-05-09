import os
import csv
import time
import argparse
try:
    import magic
except:
    pass


def arg_parser():
        parser = argparse.ArgumentParser(description = "")
        parser.add_argument('folder', nargs='+', help='Specify the folder/drive')
        args = parser.parse_args()
        return args.folder


def main():

    folder = arg_parser()
    exception_list = []
    filetype = {'BE': {'BE000000AB': 'WRI'}, '5F': {'5F27A889': 'JAR', '5F434153455F': 'CAS/CBK'}, '5A': {'5A4F4F20': 'ZOO'}, '5B': {'5B50686F6E655D': 'DUN', '5B7665725D': 'SAM', '5B5645525D': 'SAM', '5B57696E646F7773': 'CPX', '5B47656E6572616C': 'ECF', '5B4D535643': 'VCW', '5B666C7473696D2E': 'CFG'}, '24': {'24464C3240282329': 'SAV'}, '25': {'252150532D41646F': 'EPS', '25504446': 'PDF/FDF'}, '21': {'2112': 'AIN', '213C617263683E0A': 'LIB'}, '23': {'23204D6963726F73': 'DSP', '23204469736B2044': 'VMDK', '2320': 'MSI', '2321414D52': 'AMR', '233F52414449414E': 'HDR'}, '28': {'2854686973206669': 'HQX'}, '2D': {'2D6C68': 'LHA/LZH'}, '2E': {'2E524543': 'IVR', '2E7261FD00': 'RA', '2E736E64': 'AU', '2E524D4600000012': 'RA/RM/RVB'}, '2A': {'2A2A2A2020496E73': 'LOG'}, '1A': {'1A04': 'ARC', '1A02': 'ARC', '1A03': 'ARC', '1A0000040000': 'NSF', '1A350100': 'ETH', '1A08': 'ARC', '1A52545320434F4D': 'DAT', '1A0000': 'NTF', '1A0B': 'PAK', '1A09': 'ARC', '1A45DFA393428288': 'MKV'}, '58': {'5854': 'BDR', '5850434F4D0A5479': 'XPT', '582D': 'EML', '58435000': 'CAP'}, '55': {'554641C6D2C1': 'UFA', '55434558': 'UCE', '55464F4F72626974': 'DAT'}, '54': {'5468697320697320': 'INFO'}, '57': {'576F726450726F': 'LWP', '57696E5A6970': 'ZIP', '575332303030': 'WS2', '574D4D50': 'DAT'}, '56': {'56455253494F4E20': 'CTL', '564350434830': 'PCH', '56657273696F6E20': 'MIF'}, '51': {'5157205665722E20': 'QSD', '51454C20': 'QEL', '514649': 'QEMU'}, '50': {'504158': 'PAX', '5041434B': 'PAK', '504B4C495445': 'ZIP', '504B0708': 'ZIP', '504943540008': 'IMG', '504E4349554E444F': 'DAT', '50350A': 'PGM', '50455354': 'DAT', '504B0304': 'ZIP(xls/xlsx/docx/swx/jar/kwd/ODP/ODT/OTT/pptx)', '504147454455': 'DMP', '504750644D41494E': 'PGD', '504B537058': 'ZIP', '504B0506': 'ZIP', '504D4343': 'GRP', '5000000020000000': 'IDX'}, '53': {'53494554524F4E49': 'CPI', '5349542100': 'SIT', '53484F57': 'SHW', '53514C4F434F4E56': 'CNV', '537570657243616C': 'CAL', '53514C69746520666F726D6174203300': 'DB', '534D415254445257': 'SDR', '53434D49': 'IMG', '5343486C': 'AST', '5374756666497420': 'SIT'}, '52': {'52494646': '4XM/ANI/AVI/CDA/CDR/CMX/DAT/DS4/QCP/RMI/WAV', '52657475726E2D50': 'EML', '5245564E554D3A2C': 'AD', '52415A4154444231': 'DAT', '526172211A0700': 'RAR', '52454745444954': 'REG', '52545353': 'CAP'}, 'B4': {'B46E6844': 'TIB'}, 'B5': {'B5A2B0B3B3B0A5B5': 'CAL'}, 'B0': {'B04D4643': 'PWL'}, 'B1': {'B168DE3A': 'DCX'}, 'FD': {'FDFFFFFF22': 'XLS', 'FDFFFFFF23': 'XLS', 'FDFFFFFF1C000000': 'PPT', 'FDFFFFFF1F': 'XLS', 'FDFFFFFF': 'DB', 'FDFFFFFF43000000': 'PPT', 'FDFFFFFF28': 'XLS', 'FDFFFFFF29': 'XLS', 'FDFFFFFF10': 'XLS', 'FDFFFFFF04': 'SUO', 'FDFFFFFF0E000000': 'PPT'}, '1D': {'1D7D': 'WS'}, 'FF': {'FFD8FFE3': 'JPEG', 'FFD8FFE2': 'JPEG', 'FFD8FFE1': 'JPG', 'FFD8FFE0': 'JFIF/JFIF/JPEG/JPG', 'FF4B455942202020': 'SYS', 'FFD8FFE8': 'JPG', 'FF575043': 'WP', 'FFFE': 'REG', 'FF464F4E54': 'CPI', 'FFFE23006C006900': 'MOF', 'FF': 'SYS', 'FFFFFFFF': 'SYS', 'FF00020004040554': 'WKS'}, '67': {'67490000': 'SHD'}, '89': {'89504E470D0A1A0A': 'PNG'}, '3C': {'3C': 'XDR', '3C3F786D6C2076657273696F6E3D': 'MANIFEST', '3C3F786D6C2076657273696F6E3D22312E30223F3E': 'XML', '3C4D616B65724669': 'MIF', '3C21646F63747970': 'DCI'}, '80': {'80000020031204': 'ADX', '80': 'OBJ'}, '81': {'813284C18505D011': 'WAB'}, '3F': {'3F5F0300': 'GID/HLP'}, '3E': {'3E000300FEFF090006': 'WB3'}, '02': {'02647373': 'DSS'}, '03': {'03': 'DAT', '03000000': 'QPH', '0300000041505052': 'ADX'}, '00': {'00000100': 'SPL', '00004D4D585052': 'QXD', '001E849000000000': 'SNM', '00001A00051004': '123', '000100005374616E64617264204A6574204442': 'MDB', '006E1EF0': 'PPT', '00000020667479704D3441': 'M4A', '0000000C6A502020': 'JP2', '000001B3': 'MPG', '0000FFFFFFFF': 'HLP', '0000002066747970': '3GP', '0000001866747970': '3GP5', '00014241': 'ABA', '00014244': 'DBA', '0000001466747970': '3GP', '000100004D534953414D204461746162617365': 'MNY/TTF', '00001A0002100400': 'WK4', '00001A0000100400': 'WK3', '000001BA': 'MPG/VOB', '000100005374616E6461726420414345204442': 'ACCDB', '0006156100000002000004D200001000': 'DB', '0011': 'FLI', '00000200': 'CUR', '00004949585052': 'QXD'}, '01': {'01FF02040302': 'DRW', '01DA01010003': 'RGB', '0110': 'TR1', '010F0000': 'MDF'}, '07': {'0764743264647464': 'DTD', '07': 'DRW', '07534B46': 'SKF'}, '04': {'04': 'DB4'}, '08': {'08': 'DB'}, '09': {'0908100000060500': 'XLS'}, 'E9': {'E9': 'SYS/COM'}, 'E8': {'E8': 'SYS/COM'}, 'E4': {'E4525C7B8CD8A74D': 'ONE'}, 'E0': {'E01': ''}, 'E3': {'E3828596': 'PWL', 'E310000100000000': 'INFO'}, 'ED': {'EDABEEDB': 'RPM'}, 'EC': {'ECA5C100': 'DOC'}, 'EB': {'EB3C902A': 'IMG', 'EB': 'SYS/COM'}, '0C': {'0CED': 'MP'}, '0A': {'0A030101': 'PCX', '0A020101': 'PCX', '0A050101': 'PCX'}, '0F': {'0F00E803': 'PPT'}, '0D': {'0D444F43': 'DOC'}, '0E': {'0E574B53': 'WKS', '0E4E65726F49534F': 'NRI'}, '38': {'38425053': 'PSD'}, '32': {'32BE': 'WRI'}, '31': {'31BE': 'WRI'}, '30': {'3026B2758E66CF11': 'WMA/WMF', '30': 'CAT', '30314F52444E414E': 'NTF', '300000004C664C65': 'EVT'}, '37': {'377ABCAF271C': '7Z'}, '60': {'60EA': 'ARJ'}, '63': {'6375736800000002': 'CSH', '636F6E6563746978': 'VHD'}, '64': {'646E732E': 'AU', '6465780A30303900': 'dex', '64000000': 'P10', '64737766696C65': 'DSW'}, 'FE': {'FEEF': 'GHO-GHS'}, '66': {'66490000': 'SHD', '664C614300000022': 'FLAC', '66726565': 'MOV'}, '1F': {'1F8B08': 'GZ', '1FA0': 'TAR.Z', '1F9D90': 'TAR.Z'}, '68': {'68490000': 'SHD'}, '9C': {'9CCBCB8D1375D211': 'WAB'}, 'C8': {'C8007900': 'LBK'}, 'C3': {'C3ABCDAB': 'ACS'}, '78': {'78': 'DMG'}, 'C5': {'C5D0D3C6': 'EPS'}, 'CA': {'CAFEBABE': 'CLASS'}, 'CF': {'CFAD12FE': 'DBX', 'CF11E0A1B11AE100': 'DOC'}, '99': {'99': 'GPG', '9901': 'PKR'}, '91': {'91334846': 'HAP'}, '95': {'9500': 'SKR', '9501': 'SKR'}, '11': {'1100000053434341': 'PF'}, '6C': {'6C33336C': 'DBB'}, '6D': {'6D6F6F76': 'MOV', '6D646174': 'MOV'}, '8A': {'8A0109000000E108': 'AW'}, 'DB': {'DBA52D00': 'DOC'}, 'DC': {'DCFE': 'EFX', 'DCDC': 'CPL'}, '3A': {'3A56455253494F4E': 'SLE'}, '7E': {'7E424B00': 'PSP'}, '7B': {'7B0D0A6F20': 'LGC/LGD', '7B5C707769': 'PWI', '7B5C72746631': 'RTF'}, '7A': {'7A626578': 'INFO'}, '49': {'494433': 'MP3', '49545346': 'CHI/CHM', '49544F4C49544C53': 'LIT', '49443303000000': 'KOZ', '496E6E6F20536574': 'DAT', '49536328': 'CAB/HDR', '49491A0000004845': 'CRW', '492049': 'TIF/TIFF', '49492A00': 'TIF'}, '46': {'464158434F564552': 'CPE', '465753': 'SWF', '46726F6D': 'EML', '464C56': 'FLV', '464F524D00': 'AIFF'}, '47': {'47494638': 'GIF', '47504154': 'PAT'}, '44': {'44424648': 'DB', '444D5321': 'DMS', '444F53': 'ADF', '445644': 'DVR'}, '45': {'454C49544520436F': 'CDR', '454E545259564344': 'VCD', '456C6646696C6500': 'EVTX', '458600000600': 'QBB', '455646090D0AFF00': 'E01', '4552465353415645': 'DAT', '4550': 'MDI'}, '42': {'425A68': 'TAR.BZ2', '424F4F4B4D4F4249': 'PRC', '424D': 'BMP/DIB', '424547494E3A5643': 'VCF', '424C4932323351': 'BIN'}, '43': {'436174616C6F6720': 'CTF', '4350543746494C45': 'CPT', '43232B44A4434DA5': 'RTD', '434F4D2B': 'CLB', '434246494C45': 'CBD', '43524547': 'DAT', '43505446494C45': 'CPT', '435753': 'SWF', '434D5831': 'CLB', '436C69656E742055': 'DAT', '4344303031': 'ISO', '434F5744': 'VMDK', '43525553482076': 'CRU'}, '40': {'40404020000040404040': 'ENL'}, '41': {'414376': 'SLE', '41724301': 'ARC', '415647365F496E74': 'DAT', '41433130': 'DWG', '414D594F': 'SYW', '414F4C': 'ABI/ABY/BAG/IDX/IDX/IND/IND/ORG/PFC/PFC'}, 'A0': {'A0461DF0': 'PPT'}, 'A9': {'A90D000000000000': 'DAT'}, 'AC': {'ACED000573720012': 'PDB', 'AC9EBD8F0000': 'QDF'}, '77': {'77696465': 'MOV'}, '76': {'76323030332E3130': 'FLT'}, '75': {'7573746172': 'TAR'}, '74': {'74424D504B6E5772': 'PRC'}, '73': {'737A657A': 'PDB', '736C682E': 'DAT', '736C6821': 'DAT', '737263646F636964': 'CAL', '736D5F': 'PDB', '736B6970': 'MOV'}, '72': {'72696666': 'AC', '72656766': 'DAT', '727473703A2F2F': 'RAM'}, '70': {'706E6F74': 'MOV'}, '4F': {'4F504C4461746162': 'DBF', '4F67675300020000': 'OGA/OGG/OGX/OGV', '4F7B': 'DW4'}, '4D': {'4D6963726F736F667420432F432B2B20': 'PDB', '4D4C5357': 'MLS', '4D6963726F736F66742057696E646F7773204D6564696120506C61796572202D2D20': 'WPL', '4D56': 'DSN', '4D494C4553': 'MLS', '4D52564E': 'NVRAM', '4D546864': 'MID/MIDI', '4D4D002B': 'TIF/TIFF', '4D563243': 'MLS', '4D41523100': 'MAR', '4D4D002A': 'TIF', '4D534346': 'CAB', '4D5A': 'Windows/DOS executable file', '4D41723000': 'MAR', '4D444D5093A7': 'HDMP', '4D53465402000100': 'TLB', '4D535F564F494345': 'CDR/MSV', '4D6963726F736F66742056697375616C': 'SLN', '4D4D4D440000': 'MMF', '4D2D5720506F636B': 'PDB', '4D56323134': 'MLS'}, '4E': {'4E49544630': 'NTF', '4E45534D1A01': 'NSF', '4E422A00': 'JNT/JIP', '4E616D653A20': 'COD', '4E41565452414646': 'DAT'}, '4B': {'4B444D': 'VMDK', '4B47425F61726368': 'KGB', '4B490000': 'SHD'}, '4C': {'4C4E0200': 'GID/HLP', '4C01': 'OBJ', '4C5646090D0AFF00': 'E01', '4C00000001140200': 'LNK'}, '4A': {'4A47030E': 'JG', '4A4152435300': 'JAR', '4A47040E': 'JG'}, '48': {'4848474231': 'SH3', '48695021': 'hip'}, 'D7': {'D7CDC69A': 'WMF'}, 'D4': {'D42A': 'AUT'}, 'D0': {'D0CF11E0A1B11AE1': 'PPT/XLS/DOC/PPS/MSC/MTW/OPT/XLA/VSD'}, '69': {'696D' : 'Python'}}

    # If user specifies drive
    if folder[0] in ['c', 'd', 'e', 'f', 'C', 'D']:
        folder = folder[0] + ':\\'
    else:
        folder = folder[0].replace(':', ':\\')
    print 'Identifying files located in folder ' + folder

    # Identify file types. This chunk is cpu intensive. To get past the lazy stupid os.walk issues:
    # chunk the console printing
    # chunk the result file writing
    # Use nested dictionary to first match first byte and process further if match found


    for path, folders, files in os.walk(folder):
        chunk = []
        for file_name in files:
            file_num = 0
            try:
                with open(os.path.join(path, file_name)) as f:
                    hex_content = f.read().encode('hex')
            except IOError as e:
                exception_list.append(os.path.join(path, file_name))
                continue

            if hex_content and filetype.has_key(hex_content[0:2].upper()):
                for key, value in filetype[hex_content[0:2].upper()].iteritems():
                    if key in hex_content[0:7].upper() or hex_content[0:7].upper() in key and file_num == 0:
                        file_num = 1
                        chunk.append(os.path.join(path, file_name) + ' : ' + value + ' or ' +
                                     magic.from_file(os.path.join(path, file_name)).split(',')[0])

            else:
                file_num = 1
                chunk.append(os.path.join(path, file_name) + ' : ' +
                             magic.from_file(os.path.join(path, file_name)).split(',')[0])
        if chunk:
            f = open('results.txt', 'w')
            chunk = str(chunk).replace(']', '').replace('[', '').replace("'", "").replace(',', '\n')
            f.write(chunk)
            print chunk



    if len(exception_list) > 0:
        print 'These files were not processed due to permission issues'
        print exception_list


if __name__ == '__main__':
    main()
