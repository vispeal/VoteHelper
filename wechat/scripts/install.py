'''
Created on Nov 1, 2011

@author: kunli
'''
import sys
import os

PYH_FILE = 'wechat.pth'

def install_python_path():
    """
    Add project path to PATHONPATH
    """
    paths = [path for path in sys.path if path.endswith('dist-packages')]
    print paths
    if len(paths) > 0:
        dist_path = paths[0]
        pth_path = os.path.join(dist_path, PYH_FILE)
        print pth_path
        if os.path.exists(pth_path):
            os.remove(pth_path)
        print os.getcwd()
        if not os.path.exists(PYH_FILE):
            with open(PYH_FILE, "w+") as py_fp:
                print os.getcwd()
                py_fp.write(os.getcwd())
        print 'Modifying python path...'
        os.link(PYH_FILE, pth_path)

if __name__ == '__main__':
    install_python_path()
