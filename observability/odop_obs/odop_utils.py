import os


def make_folder(temp_path):
    try:
        if os.path.exists(temp_path):
            pass
        else:
            os.makedirs(temp_path)
        return True
    except:
        return False
