import base64
import socket
import threading
import json
import uuid
import datetime
import os
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from os.path import basename

thread1_finished = False
thread1_lock = threading.Lock()

def LoadData(file_name, name):
    with open(file_name) as config_file:
        config = json.load(config_file)
    return config[name]

def LoadConfigFile(file_name, name):
    try:
        with open(file_name, 'r') as config_file:
            config = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Nếu file không tồn tại hoặc có lỗi khi giải mã JSON, khởi tạo config mới với trường 'state'
        config = {name: {}}

    return config.get(name, {})

def SaveConfigFile(file_name, name, data):
    with open(file_name, 'w') as json_file:
        json.dump({name: data}, json_file, indent=4)

def set_state(filename,mailname):
    email_state = LoadConfigFile(filename, 'state')

    email_state[mailname] = 'Unread'

    SaveConfigFile(filename, 'state', email_state)

def change_element(file_name, field_name, element_name, new_value):
    config_data = LoadConfigFile(file_name, field_name)
    config_data[element_name] = new_value
    SaveConfigFile(file_name, field_name, config_data)

def check_login(user_email, password):
    email_config = LoadData('GeneralFileConfig.json', 'email')

    if (user_email == email_config["username"]) & (password == email_config["password"]):
        return True
    else:
        return False

def get_email():
    try:
        user_email = input('Email:')
        return user_email
    except KeyboardInterrupt:
        print('\nuser Email input interrupted. Exiting...')
        exit()

def get_password():
    try:
        password = input('Password:')
        return password
    except KeyboardInterrupt:
        print('\nPassword input interrupted. Exiting...')
        exit()

def connectSMTP():
    host = "127.0.0.1"
    portSMTP = 2225
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1.connect((host, portSMTP))

    response = s1.recv(1024).decode('utf-8')
    # print("Response from Server:", response)

    s1.sendall(f'EHLO {host} \r\n'.encode('utf-8'))
    response = s1.recv(1024).decode('utf-8')
    # print(response)

    return s1

def connectPOP3(email, password):
    host = "127.0.0.1"
    portPOP3 = 3335
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.connect((host, portPOP3))

    response = s2.recv(1024).decode('utf-8')
    # print("Response from Server:", response)

    s2.sendall('CAPA\r\n'.encode('utf-8'))
    response = s2.recv(1024).decode('utf-8')
    # print(response)

    s2.sendall(f'USER {email}\r\n'.encode('utf-8'))
    response = s2.recv(1024).decode('utf-8')
    # print(response)

    s2.sendall(f'PASS {password}\r\n'.encode('utf-8'))
    response = s2.recv(1024).decode('utf-8')
    # print(response)

    return s2

def CheckFileSmaller3Mb(pathfile):
    maxsize = 3 * 1024 * 1024
    if os.path.getsize(pathfile) > maxsize:
        print("File size exceeds 3MB. Please choose a smaller file.")
        return False
    else:
        return True
def send_email(sender_email, recipient_email, cc_emails, subject, message, fileList):
    try:
        s1 = connectSMTP()

        s1.sendall(f'MAIL FROM: <{sender_email}>\r\n'.encode('utf-8'))
        s1.sendall(f'RCPT TO: <{recipient_email}>\r\n'.encode('utf-8'))
        s1.sendall('DATA\r\n'.encode('utf-8'))
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        body = body_not_CC(sender_email, recipient_email, subject, message)
        if not len(cc_emails) == 0:
            msg['Cc'] = ", ".join(cc_emails)  # Thêm danh sách người CC vào trường "Cc"
            body = body_CC(sender_email, recipient_email, cc_emails, subject, message)

        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))
        for file in fileList:
            attachFile(file, msg)

        s1.sendall(f'{msg.as_string()}\r\n.\r\n'.encode('utf-8'))
        response = s1.recv(1024).decode('utf-8')
        print(response)

    except Exception as e1:
        print(f"Error: {e1}")
def send_BCC(sender_email, mailBCC, mailCC, subject, message, fileList):
    count = len(mailBCC)
    if len(mailBCC) == 0:
        return
    list_mailBCC = mailBCC[:]
    for i in range(0, count):
        send_email(sender_email, list_mailBCC[i], mailCC, subject, message, fileList)
        count -= 1
def attachFile(filepath, msg):
    with open(filepath, 'rb') as attachment:
        attachment_package = MIMEBase('application', 'octet-stream')
        attachment_package.set_payload(attachment.read())
        encoders.encode_base64(attachment_package)
        attachment_package.add_header('Content-Disposition', 'attachment; filename=' + basename(filepath))
        msg.attach(attachment_package)
def body_CC(mail_from, mail_to, cc_emails, subject, message):
    time = datetime.datetime.now()
    formatted_date = time.strftime("%A %d %B %Y %H:%M:%S")
    unique_id = uuid.uuid4()

    body = f'Message ID: < {unique_id} @ gmail.com >\r\n'
    body += f'Date: {formatted_date} +0700\r\n'
    body += 'Content-Language: en-US\r\n'
    body += f'To: <{mail_to}>\r\n'
    body += f'Cc: <{", ".join(cc_emails)}>\r\n'
    body += f'From: <{mail_from}>\r\n'
    body += f'Subject: {subject}\r\n'
    body += f'{message}\r\n'

    return body
def body_not_CC(mail_from, mail_to, subject, message):
    time = datetime.datetime.now()
    formatted_date = time.strftime("%A %d %B %Y %H:%M:%S")
    unique_id = uuid.uuid4()
    body = f'Message ID: < {unique_id} @ gmail.com >\r\n'
    body += f'Date: {formatted_date} +0700\r\n'
    body += 'Content-Language: en-US\r\n'
    body += f'To: <{mail_to}>\r\n'
    body += f'From: <{mail_from}>\r\n'
    body += f'Subject: {subject}\r\n'
    body += f'{message}\r\n'
    return body

def extract_From(response):
    try:
        if 'From: ' in response:
            return response.split('From: ')[1].split('\r\n')[0]
    except Exception as e:
        print(f'Error: {e} \r\n')

def solveAttachment(filename,data):
    folder = input("nhập folder bạn muốn lưu:")
    attachment_path = os.path.join(folder, filename)

    with open(attachment_path, 'wb') as attachment_file:
        attachment_file.write(base64.b64decode(data))
        attachment_file.close()

    print('Save successfully')

def extract_subject(response):
    try:
        if 'Subject:' in response:
            return response.split('Subject:')[1].split('\r\n')[0]
    except Exception as e:
        print(f'Error: {e} \r\n')

def extract_content(response):
    sub = extract_subject(response)
    bound = response.split('\r\n--')[1].split('==\r\n')[0]
    bound = '--' + bound + '=='
    bound_parts = response.split(bound)[1:]
    for part in bound_parts:
        if 'Message ID:' in part:
            return part.split(sub)[1].split('\r\n')[1]

def filter_email(response, config):
    email_From = extract_From(response)
    email_subject = extract_subject(response)
    email_content = extract_content(response)
    rules = config.get('rules', [])

    for rule in rules:
        if 'From' in rule and email_From in rule['From']:
            return rule['To_Folder1']

        if 'Subject' in rule and any(keyword in email_subject for keyword in rule['Subject']):
            return rule['To_Folder2']

        if 'Content' in rule and any(keyword in email_content for keyword in rule['Content']):
            return rule['To_Folder3']

        if 'Spam' in rule and any(keyword in (email_content or email_subject) for keyword in rule['Spam']):
            return rule['To_Folder4']

    return config['default']


def getFrom(filepath):
    try:
        with open (filepath, 'r') as f:
            data = f.read()
            if 'From:' in data:
                return data.split('From: <')[1].split('>\n')[0]
    except Exception as e:
        print(f'Error: {e}')
def getSubject(filepath):
    try:
        with open (filepath, 'r') as f:
            data = f.read()
            if 'Subject:' in data:
                return data.split('Subject:')[1].split('\n')[0]
    except Exception as e:
        print(f'Error: {e}')
def getResponse(s1, mail_num):
    # Gửi lệnh để lấy nội dung email
    s1.sendall(f'RETR {str(mail_num[0])}\r\n'.encode('utf-8'))
    # Nhận dữ liệu phản hồi từ server
    response = ""
    total_received = 0
    while total_received < int(mail_num[1]):
        data_chunk = s1.recv(4096).decode('utf-8')
        if not data_chunk:
            return response

        response += data_chunk

        total_received += len(data_chunk)
        if total_received >= int(mail_num[1]):
            return response

def getmail(folderpath):
    file_list = os.listdir(folderpath)
    if len(file_list) == 0:
        print("No email in this folder, please choose another folder")
    else:
        while True:
            print(f"this is list of email in {basename(folderpath)} folder:")
            for i in range(len(file_list)):
                if file_list[i] == f'{basename(folderpath)}_state.json':
                    continue
                state_file = os.path.join(folderpath, f'{basename(folderpath)}_state.json')
                config = LoadData(state_file, 'state')
                num = file_list[i].split('.msg')[0]
                From_mail = getFrom(os.path.join(folderpath, file_list[i]))
                Sub_mail = getSubject(os.path.join(folderpath, file_list[i]))
                state = config[num]
                print(f'<{state}><{From_mail}><{Sub_mail}>')
            while True:
                choose2 = input(f'Which email you want to see (press enter to exit, press 0 to back to maillist of {basename(folderpath)} folder):')
                if not choose2:
                    return
                elif int(choose2) == 0:
                    break
                else:
                    filepath = os.path.join(folderpath, file_list[int(choose2) - 1])
                    change_element(state_file, 'state', file_list[int(choose2) - 1].split('.msg')[0], 'read')

                    with open(filepath, 'r') as f:
                        data = f.read()
                        parts = data.split('\n.\n\n')
                        print(f'body of mail:\r\n {parts[0]}')
                        parts.pop()
                        for i, part in enumerate(parts):
                            if 'filename=' in part:
                                print(f'Email has attachment, do you want to install:')
                                choose3 = input('Yes, No:')
                                if choose3 == 'Yes':
                                    bound = data.split('\n--')[1].split('==\n')[0]
                                    bound = '--' + bound + '=='
                                    attachname = part.split(bound)[0].split('filename=')[1].split('\n')[0]
                                    attachdata = part.split(bound)[1]
                                    solveAttachment(attachname, attachdata)
                                elif choose3 == 'No':
                                    break
                        f.close()

def autoload(email, password):
    global thread1_finished
    # Đọc cấu hình từ file JSON
    email_config = LoadData('GeneralFileConfig.json', 'email')
    autoload_interval = float(email_config.get("autoload", 10))  # Số giây giữa mỗi lần tải về, mặc định là 10 giây

    s3 = connectPOP3(email, password)
    if s3 is None:
        print("Failed to connect to POP3 server.")
        return

    # Tạo thư mục nếu chúng không tồn tại
    folders = ['Inbox', 'Work', 'Project', 'Important', 'Spam']
    for folder in folders:
        path = os.path.join(os.getcwd(), folder)
        os.makedirs(path, exist_ok=True)

    while True:
        # Lấy danh sách tất cả các tệp trong các thư mục
        file_list = []
        for folder in folders:
            folder_path = os.path.join(os.getcwd(), folder)
            file_folder = os.listdir(folder_path)
            if f'{folder}_state.json' in file_folder:
                file_folder.pop()
            file_list += file_folder
        s3.sendall('LIST\r\n'.encode('utf-8'))
        response = s3.recv(1024).decode('utf-8')
        lines = response.splitlines()[1:]
        lines.pop()

        # Tải về email chưa tải
        for line in lines:
            numsize = line.split(' ')
            email_filename = f'{numsize[0]}.msg'
            if email_filename not in file_list:
                print(email_filename)
                s3.sendall('LIST\r\n'.encode('utf-8'))
                downLoadEmail(s3, numsize)
        with thread1_lock:
            if thread1_finished:
                print("Main thread finished. Exiting Autoload thread.")
                return
        time.sleep(autoload_interval)

def executeDownloadMail(s1):
    s1.sendall("STAT\r\n".encode('utf-8'))
    res = s1.recv(1024).decode('utf-8')

    s1.sendall('LIST\r\n'.encode('utf-8'))
    response = s1.recv(1024).decode('utf-8')

    lines = response.splitlines()[1:]
    lines.pop()
    mailList = []
    for line in lines:
        mailList.append((line.split(' ')[0], line.split(' ')[1]))
    for i in range(len(mailList)):
        downLoadEmail(s1, mailList[i])

def downLoadEmail(s1, mailList):
    try:
        filter_config = LoadData('GeneralFileConfig.json', 'folder')
        response = getResponse(s1, mailList)
        foldername = filter_email(response, filter_config)

        folderpath = os.path.join(os.getcwd(), foldername)
        os.makedirs(folderpath, exist_ok=True)
        filepath = os.path.join(folderpath, f'{mailList[0]}.msg')
        statepath = os.path.join(folderpath, f'{foldername}_state.json')
        set_state(statepath, mailList[0])
        bound = response.split('\r\n--')[1].split('==\r\n')[0]
        bound = '--' + bound + '=='
        bound_parts = response.split(bound)[1:]
        with open(filepath, 'w') as f:
            for part in bound_parts:
                if 'Message ID:' in part:
                    f.write(part.split('\r\n\r\n')[1] + '\r\n.\r\n')
                if 'Content-Disposition: attachment' in part:
                    attachment_name = part.split('attachment; ')[1].split('\r\n')[0]
                    f.write(attachment_name + '\r\n' + f'{bound}\r\n')
                    attachment_data = part.split(f'{attachment_name}')[1].split('\r\n--')[0].strip()
                    f.write(attachment_data + '\r\n.\r\n')
    except Exception as e:
        print(f"Lỗi khi lấy nội dung email: {e}")
        return None

def main(email, password):
    global thread1_finished
    while True:
        if check_login(email, password):
            break
        else:
            print('Your username or password is wrong!')
            print('Please login again!')
            email = get_email()
            password = get_password()

    print('Connecting...')
    print('Login successful')

    print("------------Menu------------:\r\n", "1. Send mail\r\n", "2. Mail list\r\n", "3. Exit\r\n")
    n = int(input('Your choice:'))
    while not n == 3:
        if n == 1:
            print("please fill some information to send mail:\r\n")
            mail_to = input("TO:")
            mail_cc = input("CC:")
            mail_cc = [] if not mail_cc else mail_cc.split(', ')

            mail_bcc = input("BCC:")
            mail_bcc = [] if not mail_bcc else mail_bcc.split(', ')

            subject = input("SUBJECT:")
            message = input("MESSAGE:")

            fileList = []
            choice = int(input("Do you want to send attachment (1. Yes, 2. No):"))
            if choice == 1:
                numsfile = input("Number of file:")
                for i in range(int(numsfile)):
                    filepath = input(f"filepath {i+1}: ")
                    while not CheckFileSmaller3Mb(filepath):
                        filepath = input(f"filepath {i+1}:")
                    fileList.append(filepath)

            count = len(mail_cc)
            send_email(email, mail_to, mail_cc, subject, message, fileList)
            for i in range(0, count):
                cc_mails_list = mail_cc[:]
                current_mail = mail_cc[i]
                cc_mails_list[i] = mail_to
                send_email(email, current_mail, cc_mails_list, subject, message, fileList)
            send_BCC(email, mail_bcc, mail_cc, subject, message, fileList)
            print("Email sent successfully!")

        if n == 2:
            s1 = connectPOP3(email, password)
            inboxPath = os.path.join(os.getcwd(), 'Inbox')
            os.makedirs(inboxPath, exist_ok=True)
            workPath = os.path.join(os.getcwd(), 'Work')
            os.makedirs(workPath, exist_ok=True)
            projectPath = os.path.join(os.getcwd(), 'Project')
            os.makedirs(projectPath, exist_ok=True)
            importantPath = os.path.join(os.getcwd(), 'Important')
            os.makedirs(importantPath, exist_ok=True)
            spamPath = os.path.join(os.getcwd(), 'Inbox')
            os.makedirs(spamPath, exist_ok=True)

            while True:
                print('This is a list of folders in your mailbox:')
                print('1.Inbox')
                print('2.Project')
                print('3.Important')
                print('4.Work')
                print('5.Spam')
                n = input('Which folder do you want to see emails in (press enter to skip):')
                if not n:
                    break
                while int(n) == 1:
                    getmail(inboxPath)
                    break
                while int(n) == 2:
                    getmail(projectPath)
                    break
                while int(n) == 3:
                    getmail(importantPath)
                    break
                while int(n) == 4:
                    getmail(workPath)
                    break
                while int(n) == 5:
                    getmail(spamPath)
                    break
            s1.close()

        print("Vui lòng chọn Menu:\r\n", "1. Để gửi email\r\n", "2. Để xem danh sách các email đã nhận\r\n", "3. Thoát")
        n = int(input())

    with thread1_lock:
        thread1_finished = True


if __name__ == "__main__":
    print("Login")
    email = get_email()
    password = get_password()
    thread1 = threading.Thread(target=main, args=(email, password))
    thread2 = threading.Thread(target=autoload, args=(email, password))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

