from typing import Union

from pydicom import config, FileDataset
from pydicom import dcmread

from pydicom.dicomdir import DicomDir

# To ensure we have correctly formatted DICOM files
# config.settings.reading_validation_mode = config.RAISE


def get_dicos_value(ds, tag1, tag2):
    value = None
    try:
        value = str(ds[tag1, tag2].value)
    except KeyError:
        print("Value missing + (" + str(tag1) + ", " + str(tag2) + ")")
    return value


# TDR Requirements
def print_all_fields(ds: Union[FileDataset, DicomDir]):
    print("***** ALL FIELDS (TDR Requirements): *****")
    print("*** OOI module ***")
    print("OOI ID = " + get_dicos_value(ds, 0x0010, 0x0020))
    print("Issuer of OOI ID =" + get_dicos_value(ds, 0x0010, 0x0021))
    print("Type of OOI ID =" + get_dicos_value(ds, 0x0010, 0x0022))
    print("Other OOI IDs Sequence =" + get_dicos_value(ds, 0x0010, 0x1002))
    print(">OOI ID =" + get_dicos_value(ds, 0x0010, 0x0020))
    print(">Issuer of OOI ID =" + get_dicos_value(ds, 0x0010, 0x0021))
    print(">Type of OOI ID =" + get_dicos_value(ds, 0x0010, 0x0022))
    print("Algorithm Routing Code sequence = " + get_dicos_value(ds, 0x4010, 0x1064))
    print(">Code Value = " + get_dicos_value(ds, 0x0008, 0x0100))
    print(">Coding Scheme Designator = " + get_dicos_value(ds, 0x0008, 0x0102))
    print(">Code Scheme Version = " + get_dicos_value(ds, 0x0008, 0x0103))
    print(">Code Meaning = " + get_dicos_value(ds, 0x0008, 0x0104))
    print("OOI Type = " + get_dicos_value(ds, 0x4010, 0x1042))
    print()

    print("*** Scan module ***")
    print("Scan Instance UID = " + get_dicos_value(ds, 0x0020, 0x000D))
    print("Scan Date = " + get_dicos_value(ds, 0x0008, 0x0020))
    print("Scan Time = " + get_dicos_value(ds, 0x0008, 0x0030))
    print("Scan Type = " + get_dicos_value(ds, 0x4010, 0x1048))
    print("Readable scan ID = " + get_dicos_value(ds, 0x0020, 0x0010))
    print("Referenced Scan Sequence = " + get_dicos_value(ds, 0x0008, 0x1110))
    print("Referenced SOP Class UID = " + get_dicos_value(ds, 0x0008, 0x1150))
    print("Referenced SOP Instance UID = " + get_dicos_value(ds, 0x0008, 0x1155))
    print()

    print("*** Series module ***")
    print("Series Instance UID = " + get_dicos_value(ds, 0x0020, 0x000E))
    print("Series Date = " + get_dicos_value(ds, 0x0008, 0x0021))
    print("Series Time = " + get_dicos_value(ds, 0x0008, 0x0031))
    print("Modality = " + get_dicos_value(ds, 0x0008, 0x0060))
    print("Acquisition Status = " + get_dicos_value(ds, 0x4010, 0x1044))
    print()

    print("*** General equipment module ***")
    print("Manufacturer = " + get_dicos_value(ds, 0x0008, 0x0070))
    print("Machine location = " + get_dicos_value(ds, 0x0008, 0x0080))
    print("Machine Address = " + get_dicos_value(ds, 0x0008, 0x0081))
    print("Machine ID = " + get_dicos_value(ds, 0x0008, 0x1010))
    print("Manufacturer's Model Name = " + get_dicos_value(ds, 0x0008, 0x1090))
    print("Device Serial Number = " + get_dicos_value(ds, 0x0018, 0x1000))
    print("Software Versions = " + get_dicos_value(ds, 0x0018, 0x1020))
    print("Date of Last Calibration = " + get_dicos_value(ds, 0x0018, 0x1200))
    print("Time of Last Calibration = " + get_dicos_value(ds, 0x0018, 0x1201))
    print("Pixel Short Padding Value = " + get_dicos_value(ds, 0x0028, 0x0120))
    print("Pixel Long Padding Value = " + get_dicos_value(ds, 0x0028, 0x1120))
    print("Pixel Double Padding Value = " + get_dicos_value(ds, 0x0028, 0x2120))
    print("Pixel Float Padding Value = " + get_dicos_value(ds, 0x0028, 0x3120))
    print()

    print("*** SOP common module ***")
    print("SOP Class UID = " + get_dicos_value(ds, 0x0008, 0x0016))
    print("SOP Instance UID = " + get_dicos_value(ds, 0x0008, 0x0018))
    print("Specific Character Set = " + get_dicos_value(ds, 0x0008, 0x0005))
    print("Instance Creation Date = " + get_dicos_value(ds, 0x0008, 0x0012))
    print("Instance Creation Time = " + get_dicos_value(ds, 0x0008, 0x0013))
    print("DICOS Version = " + get_dicos_value(ds, 0x4010, 0x103A))
    print(
        ">Purpose of reference code sequence = " + get_dicos_value(ds, 0x0040, 0xA170)
    )
    print(">>Code Value = " + get_dicos_value(ds, 0x0008, 0x0100))
    print(">>Coding Scheme Designator = " + get_dicos_value(ds, 0x0008, 0x0100))
    print(">> = " + get_dicos_value(ds, 0x0008, 0x0100))
    print("aaaaaaaa = " + get_dicos_value(ds, 0x0008, 0x0100))
    print("aaaaaaaa = " + get_dicos_value(ds, 0x0008, 0x0100))
    print("aaaaaaaa = " + get_dicos_value(ds, 0x0008, 0x0100))
    print("aaaaaaaa = " + get_dicos_value(ds, 0x0008, 0x0100))
    print("aaaaaaaa = " + get_dicos_value(ds, 0x0008, 0x0100))
    print("aaaaaaaa = " + get_dicos_value(ds, 0x0008, 0x0100))
    print("aaaaaaaa = " + get_dicos_value(ds, 0x0008, 0x0100))
    print("aaaaaaaa = " + get_dicos_value(ds, 0x0008, 0x0100))
    print("aaaaaaaa = " + get_dicos_value(ds, 0x0008, 0x0100))
    print()

    print("*** CT image module ***")
    print("Image type = " + get_dicos_value(ds, 0x0008, 0x0008))
    print("Sample per pixel = " + get_dicos_value(ds, 0x0028, 0x0002))
    print("Bits allocated = " + get_dicos_value(ds, 0x0028, 0x0100))
    print("Bits stored = " + get_dicos_value(ds, 0x0028, 0x0101))
    print()

    print("*** Threat Detection Report module ***")
    print("TDR type = " + get_dicos_value(ds, 0x4010, 0x1027))
    print("Operator ID = " + get_dicos_value(ds, 0x0008, 0x1072))
    print("Alarm decision time = " + get_dicos_value(ds, 0x4010, 0x102B))
    print("Alarm decision = " + get_dicos_value(ds, 0x4010, 0x1031))
    print("Abort flag = " + get_dicos_value(ds, 0x4010, 0x1024))
    print("Abort reason = " + get_dicos_value(ds, 0x4010, 0x1021))
    print("Threat Detection Algo and Version = " + get_dicos_value(ds, 0x4010, 0x1029))
    print("Nb of total objects = " + get_dicos_value(ds, 0x4010, 0x1033))
    print("Number of alarm objects = " + get_dicos_value(ds, 0x4010, 0x1034))
    print("Total processing time = " + get_dicos_value(ds, 0x4010, 0x1069))
    print("Potential Threat Object ID = " + get_dicos_value(ds, 0x4010, 0x1010))
    print("Threat category = " + get_dicos_value(ds, 0x4010, 0x1012))
    print("ATD Assessment flag = " + get_dicos_value(ds, 0x4010, 0x1015))
    print("Total processing time = " + get_dicos_value(ds, 0x4010, 0x1069))
    print("Threat ROI Voxel sequence= " + get_dicos_value(ds, 0x4010, 0x1001))
    print("Mass = " + get_dicos_value(ds, 0x4010, 0x1017))
    print("Density of the PTO = " + get_dicos_value(ds, 0x4010, 0x1018))
    print(
        "Threat Sequence = " + get_dicos_value(ds, 0x4010, 0x1011)
    )  # print(ds[0x4010, 0x1011].value)
    print()


if __name__ == "__main__":
    dicos_file = dcmread("/home/S0119085/Bureau/DICOS/DataFiles/AIT2DwithTDR/tdr.dcs")
    # ds = dcmread("/home/S0119085/Bureau/DICOS/DE_140KV_1_0_D50F_0034.dcs")

    print_all_fields(dicos_file)
    # all the fields + values
    # print(ds)
    # print("***************")
    # print("***************")

    # get the DICOSVersion via keyword or tag
    # print(ds["DICOSVersion"])
    # print(ds[0x4010, 0x103A])

    # Changing values
    # ds.LowEnergyDetectors = "N"
    # ds.HighEnergyDetectors = "Y"

    # print(ds["LowEnergyDetectors"])

    # Saving
    # ds.save_as("out.dcs")
