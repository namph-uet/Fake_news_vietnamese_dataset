import csv

# with open('politifact_comment_no_ignore.csv', mode='a', encoding='utf8', newline='') as csv_file:
#     fieldnames = ['id', 'comment']
#     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#     with open('comment.csv', mode='r', encoding='utf8') as comment_file:
#                 csv_reader = csv.DictReader(comment_file)
#                 all_comment = ''
#                 first = True
#                 for row in csv_reader:
#                     comment = row['comment']
#                     if comment != '':
#                         if first:
#                             all_comment += comment
#                             first = False
#                         else: all_comment += '::'+ comment
#                 print(all_comment)
#                 writer.writerow({'id': '10161249413625620', 'comment': all_comment})

with open('politifact_comment_no_ignore.csv', mode='r', encoding='utf8') as csv_file:
    fieldnames = ['id', 'comment']
    csv_reader = csv.DictReader(csv_file)
    count = 0
    for row in csv_reader:
        if row['comment']!='': count+=1

    print(count)
                