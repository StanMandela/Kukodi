'''Properties model: Class to manage house data'''
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
from flask import jsonify, request
from app.api.v1.models.database import init_db
from app.api.v1.models.landlord_models import token_verification
from instance.config import Config
JWT_SECRET = Config.SECRET_KEY

INIT_DB = init_db()

class HouseRecords():
    """ Create a model that stores property data"""

    def __init__(self):
        """initialize the database and argument variables"""
        self.database = INIT_DB

    def register_house(self, house_number, house_type, rent_amount):
        """ Add a new property """

        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split( )[1]
        
        decoded_token = jwt.decode(auth_token, JWT_SECRET, algorithms='HS256')
        landlord_id = decoded_token['sub']

        property_id_query = ('SELECT property_id FROM property WHERE landlord_id='%(landlord_id)s')

        payload = {
            "property_id": property_id,
            "house_number": house_number,
            "house_type": house_type,
            "rent_amount": rent_amount
        }

        query = """INSERT INTO houses (rent_amount, house_type, house_number, property_id) VALUES (%(rent_amount)s,%(house_type)s,%(house_number)s, %(property_id)s);"""

        cur = self.database.cursor()
        cur.execute(query, payload)
        self.database.commit()

        return jsonify({"message": ("house %s %s successfully registered")%(house_type, house_number)}), 201

    def view_houses(self):
        '''View all houses '''
        try:
            cur = self.database.cursor(cursor_factory=RealDictCursor)
            cur.execute("""  SELECT * FROM houses """)
            data = cur.fetchall()

            if data == None:
                return jsonify({"message":"no houses found"})

            return jsonify({"houses": data})

        except (psycopg2.Error) as error:
            return jsonify(error)

    def view_house(self, house_id):
        ''' View a particular house '''
        try:
            cur = self.database.cursor(cursor_factory=RealDictCursor)
            cur.execute("""  SELECT * FROM houses WHERE house_id = '%s' """ % (house_id))
            data = cur.fetchone()

            if data == None:
                return jsonify({"message":"property does not exist"})

            return jsonify({"houses ": data})

        except (psycopg2.Error) as error:
            return jsonify(error)
    
    def view_house_by_number(self, house_number):
        '''View a particular property by name(To allow for search)'''
        try:
            cur = self.database.cursor(cursor_factory=RealDictCursor)
            cur.execute("""  SELECT * FROM houses WHERE house_number = '%s' """ % (house_number))
            data = cur.fetchone()

            if data == None:
                return jsonify({"message":"house does not exist"})

            return jsonify({"houses ": data})

        except (psycopg2.Error) as error:
            return jsonify(error)