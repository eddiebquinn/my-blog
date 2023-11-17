import sys
import gnupg

def main():
    raw_data = RawData(file=True).string
    gpg_client = Gpg_client()
    message = gpg_client.extract_content(raw_data)

    return message

class Gpg_client:

    def __init__(self):
        self.gpg = gnupg.GPG()
    
    def extract_content(self, signed_message:str):
        ## Strip out begining
        content_start_index = signed_message.find('\n\n')
        if content_start_index != -1:
            content = signed_message[content_start_index + 2:]

        ## Strip out signature at the end
        sig_start_index = content.rfind("-----BEGIN PGP SIGNATURE-----")
        if sig_start_index != -1:
            content = content[:sig_start_index]
        
        return content


class RawData:

    def __init__(self, file:bool = False):
        self.file = file
        self.string = self.extract_string()
    
    def extract_string(self):
        if self.file:
            path = sys.argv[1]
            with open(path, 'r') as file:
                contents = file.read()
                return contents
        else:
            return sys.argv[1]

if __name__ == "__main__":
    message = main()
    print(message)