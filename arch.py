import os
import  json
import shutil
import subprocess 

from flask import Flask,escape,request,send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app, support_credentials=True)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

#helper functions
def authCheck(key):
    return key == '4d069b4e77b1d1804bead1d3bea762b8'

def extract(path,rar_file):
    if ".rar" in rar_file:
        return "unrar x -r "+path+'/'+rar_file+" "+path+'/'
    elif ".zip" in rar_file:
        return "unzip "+path+'/'+rar_file+" -d "+'/'

def download(folder):
    return "zip -r {}.zip {}".format(folder.split('/')[-1],folder)
    
def compress(folder):
    '''Compresses the file/folder and saves in
    the same  directory
    @return : output, err'''
    cmd = "zip -r {}.zip {}".format(folder,folder)
    print(cmd)
    time = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
    # output, err = time.communicate()  
    return time.communicate()  
#end of helper functions

@app.route('/')
def home():
    return json.dumps("Extension of my cloud")

@app.route('/login',methods=['POST'])
def login():
    '''It handles database connections for login'''
    pass

@app.route('/root',methods=['POST'])
def hello():
    ''' This route provides the contents of the root directory'''
    if not authCheck(request.headers['Auth']):
        return json.dumps({'message':'unauthorized user'}),401
    arr = os.listdir('/root')
    return json.dumps([a for a in arr if not  a.startswith('.')])  

@app.route('/root/<folder>',methods=['POST'])
def folderAccess(folder):
    '''This will return the contents of the folder as per
    the value in Folder key of the request header '''
    if not authCheck(request.headers['Auth']):
        return json.dumps({'message': 'Unauthorized Access'})

    if not folder == 'folder':
        return json.dumps({'message':'Bad Request'}),500

    try:
        if request.headers['Folder']:
            arr = os.listdir(request.headers['Folder'])
            return json.dumps([a for a in arr if not a.startswith('.')])
        raise Exception('Folder not found')
    except Exception as e:
        return json.dumps({'message':'Folder Not found'}),404

@app.route('/content/<file>',methods=['POST'])
def content(file):
    '''Returns the content of the file so that it can be
    displayed in the vs code '''
    if not authCheck(request.headers['Auth']):
        return json.dumps({'message':'Unauthorized User'})
    try:
        file = open(request.headers['file'],'r')
        content = file.read()
        file.close()
        print(content)
        return json.dumps({'file':content})
    except:
        return json.dumps({'message':'FolderNot found'}),404

@app.route('/update/<file>',methods=['POST'])
def update(file):
    '''Updates the contents of the file'''
    try:
        if not authCheck(request.headers['Auth']):
            return json.dumps({'message':'Unauthorized User'})
        try:
            f = open(request.headers['file'],'wb')
            f.write(request.data)
            f.close()
            return json.dumps({'message':'success'})
        except:
            return json.dumps({'message':'File not found'})
    except:
        return json.dumps({'message':'Unauthorized User'})
        
@app.route('/create/dir',methods=['POST'])
def create_dir():
    '''will create directory'''
    try:
        if not authCheck(request.headers['Auth']):
            return json.dumps({'message':'Unauthorized User'})
        try:
            os.mkdir(request.headers['dir'])
            return json.dumps({'message':'success'})
        except OSError:
            return json.dumps({'message':"Creation of the directory failed"}),500
    except:
        return json.dumps({'message':'Unauthorized User'})
        
@app.route('/create/file',methods=['POST'])
def create_file():
    '''will create file'''
    try:
        if not authCheck(request.headers['Auth']):
            return json.dumps({'message':'Unauthorized User'})
        try:
            f = open(request.headers['file'],'w')
            f.close()
            return json.dumps({'message':'success'})
        except OSError:
            return json.dumps({'message':"Creation of the file failed"}),500
    except Exception as e:
        print(e)
        return json.dumps({'message':'Unauthorized User'})
        
@app.route('/delete/file',methods=['POST'])
def deleteFile():
    try:
        if not authCheck(request.headers['Auth']):
            return json.dumps({'message':'Unauthorized User'})
        try:
            os.remove(request.headers['file'])
            return json.dumps({'message':'Deleted'})
        except OSError:
            try:
                os.rmdir(request.headers['file'])
                return json.dumps({'message':'Deleted'})
            except Exception as e:
                try:
                    shutil.rmtree(request.headers['file'])
                    return json.dumps({'message':'Deleted'})
                except: 
                    return json.dumps({'message':"Unable to delete file"}),500
    except Exception as e:
        print(e)
        return json.dumps({'message':'Unauthorized User'})
        
@app.route('/delete/dir',methods=['POST'])
def deleteDirectory():
    try:
        if not authCheck(request.headers['Auth']):
            return json.dumps({'message':'Unauthorized User'})
        try:
            os.rmdir(request.headers['dir'])
            return json.dumps({'message':'Deleted'})
        except:
            try:
                shutil.rmtree(request.headers['dir'])
                return json.dumps({'message':'Deleted'})
            except: 
                return json.dumps({'message':"Unable to delete file"}),500
    except Exception as e:
        print(e)
        return json.dumps({'message':'Unauthorized User'})

@app.route('/unpack',methods=['POST'])
def unpack():
    try:
        if not authCheck(request.headers['Auth']):
            return json.dumps({'message':'Unauthorized User'})
        try:
            if request.headers['command'] == "Extract":
                # cmd = "unrar x -r "+request.headers['dest']+request.headers['file']+" "+request.headers['dest']
                cmd = extract(request.headers['dest'],request.headers['file'])
                print(cmd)
            elif request.headers['command'] == "Download":
                print('herer')
                print(request.headers['folder'])
                cmd = download(request.headers['folder'])
                print(cmd)
                time = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
                output, err = time.communicate()
                print(request.headers['folder'].split('/')[-1]+'.zip')
                return send_file(os.path.join(OUTPUT_DIR, request.headers['folder'].split('/')[-1]+'.zip'))
            time = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
            output, err = time.communicate()
            print(output)
            return json.dumps("It is"+ str(output))
        except Exception as e:
            print(e)
            return json.dumps({'message':"Unable to extract file"}),500
    except:
        return json.dumps({'message':'Unauthorized User'})
        
@app.route('/download/<key>')
def downloadFile(key):
    if not authCheck(key):
        return json.dumps({'message':'Unauthorized User'})
    filename = request.args.get("filename")
    return send_file(filename)
    # return send_file(os.path.join(OUTPUT_DIR, filename))
    
@app.route('/compress/<key>',methods=['POST'])
def compress_file(key):
    if not authCheck(key):
        return json.dumps({'message':'Unauthorized User'})
    try:
        if not authCheck(request.headers['Auth']):
            return json.dumps({'message':'Unauthorized User'})
    except:
        return json.dumps({'message':'Unauthorized User'})
    try:
        out = compress(request.headers['folder'])
        return json.dumps({'message':'success'})
    except Exception as e:
        print('last exception'+e.message)
        return json.dumps({'error':e.message})
        
@app.route('/miscellaneous/<key>',methods =['POST'])
def miscellaneous(key):
    if not authCheck(key):
        return json.dumps({'message':'Unauthorized User'})
    try:
        if not authCheck(request.headers['Auth']):
            return json.dumps({'message':'Unauthorized User'})
    except:
        return json.dumps({'message':'Unauthorized User'})
    
    try:
        if request.headers['command'] == 'Rename':
            os.rename(request.headers['filename'],request.headers['newFileName'])
            return json.dumps({'message':'Rename successfull'})
    except Exception as e:
        return json.dumps({'message':'error'})
    
        
if __name__ =="__main__":
    app.run(host='0.0.0.0',debug=True)
