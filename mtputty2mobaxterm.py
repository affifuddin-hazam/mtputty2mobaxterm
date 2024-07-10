import xml.etree.ElementTree as ET

def parse_mtputty_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    sessions = []

    def parse_node(node, parent_folder=""):
        session = node.find('.//SavedSession')
        if session is not None:
            display_name = node.find('.//DisplayName').text
            server_name = node.find('.//ServerName').text
            port = node.find('.//Port').text if node.find('.//Port') is not None else '22'
            username = node.find('.//UserName').text if node.find('.//UserName') is not None else ''

            
            if port == '0':
                port = '22'

            sessions.append({
                'name': display_name,
                'host': server_name,
                'port': port,
                'username': username,
                'parent_folder': parent_folder 
            })

        for child_node in node.findall('.//Node'):
            if child_node.get('Type') == "0":  
                folder_name = child_node.find('.//DisplayName').text
                new_parent_folder = f"{parent_folder}/{folder_name}" if parent_folder else folder_name
                parse_node(child_node, new_parent_folder)
            elif child_node.get('Type') == "1": 
                parse_node(child_node, parent_folder)

    for server in root.findall('.//Node'):
        if server.get('Type') == "0": 
            folder_name = server.find('.//DisplayName').text
            parse_node(server, folder_name)

    return sessions

def create_mobaxterm_session_string(session):
    ip_address = session['host']
    return (
        f"{ip_address}= #109#0%{ip_address}%{session['port']}%%%-1%-1%%%%%0%-1%0%%%-1%0%0%0%%1080%%0%0%1%#MobaFont%10%0%0%-1%15%236,236,236%30,30,30%180,180,192%0%-1%0%%xterm%-1%0%"
        f"_Std_Colors_0_%80%24%0%1%-1%<none>%%0%0%-1%-1#0# #-1"
    )

def create_mobaxterm_ini(sessions, ini_file):
    with open(ini_file, 'w') as configfile:
        
        configfile.write("[Bookmarks]\n")
        configfile.write("SubRep=\n")
        configfile.write("ImgNum=42\n")
        
        folder_dict = {}
        folder_count = 1

        
        folder_sessions = {}

        
        for session in sessions:
            parent_folder = session['parent_folder']
            if parent_folder not in folder_sessions:
                folder_sessions[parent_folder] = []
            folder_sessions[parent_folder].append(session)

        
        for parent_folder, folder_sessions_list in folder_sessions.items():
            if parent_folder == "":
                continue  

            configfile.write(f"[Bookmarks_{folder_count}]\n")
            configfile.write(f"SubRep={parent_folder}\n")
            configfile.write(f"ImgNum=42\n")
            
            for session in folder_sessions_list:
                configfile.write(create_mobaxterm_session_string(session) + "\n")

            folder_count += 1

        
        for session in sessions:
            if session['parent_folder'] == "":
                configfile.write(f"[Bookmarks_{folder_count}]\n")
                configfile.write(f"SubRep=\n")  
                configfile.write(f"ImgNum=41\n")
                configfile.write(create_mobaxterm_session_string(session) + "\n")
                folder_count += 1

        print(f"Converted {len(sessions)} sessions from MTPuTTY to MobaXterm.")

def convert_mtputty_to_mobaxterm(mtputty_file, mobaxterm_file):
    sessions = parse_mtputty_xml(mtputty_file)
    create_mobaxterm_ini(sessions, mobaxterm_file)


if __name__ == "__main__":
    mtputty_file = 'mtputty.xml'
    mobaxterm_file = 'mtputty_2_mobaxterm.mxtsessions'
    convert_mtputty_to_mobaxterm(mtputty_file, mobaxterm_file)
