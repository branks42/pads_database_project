import os
import datetime
import mysql.connector
import pandas as pd

from qr_rectify import scan_rectify_image


def main():

    # The directory to parse
    dirName = 'Name of Directory here'

    # Use pandas to read excel file
    # May need to turn tables into actual tables in Excel itself
    # https://stackoverflow.com/questions/43367805/pandas-read-excel-multiple-tables-on-the-same-sheet
    excel_file = pd.ExcelFile('Excel FileName').parse('Sheet Name')

    # Database connection
    pad_db = mysql.connector.connect(
        host='Host',
        user='User',
        passwd='Password',
        database='DB Name'
    )

    # Cursor set to a dictionary cursor(For putting data in db)
    cursor = pad_db.cursor(dictionary=True)

    # Get the list of all files in directory tree at given path
    list_of_paths = list()
    for (dirpath, dirnames, filenames) in os.walk(dirName):
        list_of_paths += [os.path.join(dirpath, file)
                          for file in filenames]

    # id # start
    id_number = 1
    lost_qr_count = 1

    # Loop through list_of_paths
    for elem in list_of_paths:

        # Dictionary for each loop
        database_entry = {}
        # Find full paths for picture_1_location
        if elem.endswith('.jpg') is True:
            database_entry['id'] = id_number
            database_entry['picture_1_location'] = elem
            # Setting pad_number to the results of the QR scanner
            database_entry['pad_number'] = scan_rectify_image(elem)
        # If no images are found inside subfolders, we ignore
        elif elem.endswith('.jpg') is False:
            continue

        # Split the file path into seperate chunks
        split_path = elem.split('/')

        # Looking for all Analyst folders in split_path
        if 'Analyst' in split_path[1]:
            database_entry['user_name'] = split_path[1]
            database_entry['notes'] = split_path[2]
            # test_name is a constant
            database_entry['test_name'] = '12LanePADKenya2015'
            # date_of_creation is also a constant
            database_entry['date_of_creation'] = datetime.datetime.now()

        # Setting a variable to ensure the pad_number corresponds to the PAD #
        # in the excel file
        try:
            mask = excel_file['PAD #'] == int(database_entry['pad_number'])
            # Variable to return the whole row of matching pad_number
            filtered_row = excel_file[mask]
            try:
                # Appending the Sample ID to the notes
                database_entry['notes'] += ' - ' + \
                    filtered_row['Sample ID'].values[0]
                database_entry['sample_name'] = filtered_row['Labelled As'].values[0]
            # If there are no matching pad_numbers in the excel file, we ignore it
            except IndexError:
                database_entry['notes'] = database_entry['notes']
                database_entry['sample_name'] = None
        except TypeError:
            database_entry['notes'] = database_entry['notes']
            database_entry['sample_name'] = None
            # Count the amount of photos we don't get QR code
            print(str(lost_qr_count) + ' QR codes could not be read.')
            percentage_lost = (lost_qr_count * 100)/id_number
            # Print the percentage of images that are missing metadata
            print(str(percentage_lost) +
                  '% of images missing metadata.')
            lost_qr_count += 1

        # Adding 1 to the id count
        id_number += 1

        # commands to insert values into the database
        mysql_command = ("INSERT INTO padtest (id, sample_name, test_name, user_name, date_of_creation, picture_1_location, notes, pad_number) "
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")

        # values for placeholders in above command
        data = (database_entry['id'], database_entry['sample_name'], database_entry['test_name'], database_entry['user_name'],
                database_entry['date_of_creation'], database_entry['picture_1_location'], database_entry['notes'], database_entry['pad_number'])

        cursor.execute(mysql_command, data)
        pad_db.commit()
        print(database_entry)


if __name__ == '__main__':
    main()
