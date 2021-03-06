'''Model to manage billing records'''
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
from datetime import datetime, timedelta
from flask import jsonify
from app.api.v1.models.database import init_db
from app.api.v1.models.landlord_models import token_verification
from instance.config import Config
JWT_SECRET = Config.SECRET_KEY

INIT_DB = init_db()

class BillingRecords():
    """ Create a model that creates monthly bills"""

    def __init__(self):
        """initialize the database and argument variables"""
        self.database = INIT_DB

    def billing(self):
        """ create a bill """

        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split( )[1]
        
        decoded_token = jwt.decode(auth_token, JWT_SECRET, algorithms='HS256')
        landlord_id = decoded_token['sub']

        property_id_query = ("SELECT property_id FROM property WHERE landlord_id='%(landlord_id)s'")

        cur = self.database.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, property_id_query)
        data = cur.fetchone()

        property_id = data['property_id']

        house_details_query = ("SELECT * FROM houses WHERE property_id='%(property_id)s'")

        cur = self.database.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, property_id_query)
        data = cur.fetchall()

        house_no = data["house_no"]
        amount_payable = data["rent_amount"]
        house_id = data["house_id"]

        date = (datetime.now() + datetime.timedelta(days=30)).strftime("%M")
        billing_id = date + "/"+ house_no

        payload = {
            "house_no": house_no,
            "house_id": house_id,
            "amount_payable": amount_payable,
            "billing_id":billing_id
        }


        query = """INSERT INTO billing (house_no, amount_payabe, house_id, billing_id) VALUES (%(house_no)s,%(amount_payable)s,%(house_id)s, %(billing_id)s);"""


        cur = self.database.cursor()
        cur.execute(query, payload)
        self.database.commit()

        return jsonify({"message": ("bill %s successfully created")%(billing_id)}), 201

    def view_bills(self):
        '''View all bills'''
        try:
            cur = self.database.cursor(cursor_factory=RealDictCursor)
            cur.execute("""  SELECT * FROM billing """)
            data = cur.fetchall()

            if len(data) == 0:
                return jsonify({"message":"no bills found"})

            return jsonify({"bills": data})

        except (psycopg2.Error) as error:
            return jsonify(error)

    def view_bill(self, billing_id):
        '''View a particular bill'''
        try:
            cur = self.database.cursor(cursor_factory=RealDictCursor)
            cur.execute("""  SELECT * FROM billing WHERE billing_id = '%s' """ % (billing_id))
            data = cur.fetchone()

            if data == None:
                return jsonify({"message":"bill not yet created"})

            return jsonify({"bills ": data})

        except (psycopg2.Error) as error:
            return jsonify(error)