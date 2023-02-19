from flask_restful import Api , Resource
import pymongo
from flask import Flask , jsonify , request
import hashlib
from bson.json_util import dumps
app = Flask(__name__)
api = Api(app)

## connecting to the database ( mongo )
client = pymongo.MongoClient('mongodb://localhost:27017/' , username='root' , password='password'   )  ## mongo auth ##
db = client.test_database #### data base name ###
collection=db["posts"] #### collection name ### 

def verifyPw ( username , password) : 
    user_record = db.posts.find_one({'username': username}) 
    pw = dumps(user_record['password'])
    pw=str(pw)
    pass_test=  hashlib.sha256(str(password).encode('utf-8')).hexdigest()  ## hashing the given password ##
    pass_test = f'"{pass_test}"'   # " password  "
    if pass_test == pw:
        print(True )
        return True 
    else : 
      print(False)
      print( pass_test  )
      False


def count_tokens (username) : 
    user_record = db.posts.find_one({'username': username})
    tokens = dumps(user_record['Tokens'])
    return tokens

### create an " account " ######""
class Register(Resource): 
    def post(self): 
        ### getting the data 
        posteData = request.json
        username = posteData["username"]
        password = posteData["password"]
        hashed_pw=  hashlib.sha256(str(password).encode('utf-8')).hexdigest() 
        post = {
            "username" : username
            , "password" : hashed_pw , 
            "Sentence": "",
            "Tokens":6
           
        }
        posts = db.posts 
        post_id = posts.insert_one(post).inserted_id

    
        retjson={
            "status":200 , 
            "msg" : " you successfully signed up "
        }
        return jsonify(retjson) 

### storing a sentence ### 
class Store(Resource) : 
    def post(self) : 
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"] 
    
        correct_pw = verifyPw(username , password) 
        if not correct_pw : 
            retJson = {
                "status" : 302 
            }
            return jsonify(retJson)
       
        num_tokens = count_tokens(username) 
        num_tokens = int(num_tokens)
        if  num_tokens <= 0 : 
            retJson = {
                "status" : 301 
            }
            return jsonify(retJson)

        db.posts.update_one({ "username" : username } , {
            '$set' :{
                "sentence":sentence , 
                "Tokens": num_tokens-1 
                }  } )
        retjson = {
            "status": 200 ,
            "msg" : "saved successfully"
        }
        return jsonify(retjson)

##### geting the sentence ####
class get(Resource) : 
    def post(self): 
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        correct_pw = verifyPw(username , password) 
        if not correct_pw : 
            retJson = {
                "status" : 302 
            }
            return jsonify(retJson)
        num_tokens = count_tokens(username) 
        num_tokens = int(num_tokens)
        if  num_tokens <= 0 : 
            retJson = {
                "status" : 301 
            }
            return jsonify(retJson)
        user_record = db.posts.find_one({'username': username})
        sentence = dumps(user_record['sentence'])
        sentence=str(sentence)
        retjson = {
            "status": 200 ,
            "msg" : sentence
        }
        return jsonify(retjson)



api.add_resource(Register ,  '/register')
api.add_resource(Store, '/store')
api.add_resource(get, '/get')



if __name__ == "__main__" : 
    app.run(debug=True) 



