from flask import Flask, request, render_template
import MySQLdb
import cv2
import numpy as np
from deepface import DeepFace

app = Flask(__name__)

# MySQL Configuration
db = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="sqlintern",
    db="customer_db"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_customer', methods=['POST'])
def add_customer():
    name = request.form['name']
    image = request.files['image'].read()

    cursor = db.cursor()
    query = "INSERT INTO customers (name, image) VALUES (%s, %s)"
    cursor.execute(query, (name, image))
    db.commit()
    cursor.close()

    return "Customer added successfully!"

@app.route('/compare_images', methods=['POST'])
def compare_images():
    image1_id = int(request.form['image1_id'])
    image2_id = int(request.form['image2_id'])

    cursor = db.cursor()
    # Fetch images from the database
    cursor.execute("SELECT image FROM customers WHERE id = %s", (image1_id,))
    image1_data = cursor.fetchone()

    cursor.execute("SELECT image FROM customers WHERE id = %s", (image2_id,))
    image2_data = cursor.fetchone()

    cursor.close()

    if not image1_data or not image2_data:
        return "One or both customer IDs do not exist!"

    # Decode image blobs
    image1 = cv2.imdecode(np.frombuffer(image1_data[0], np.uint8), cv2.IMREAD_COLOR)
    image2 = cv2.imdecode(np.frombuffer(image2_data[0], np.uint8), cv2.IMREAD_COLOR)

    # Convert the images to RGB (DeepFace expects RGB format)
    image1_rgb = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
    image2_rgb = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)

    # Save the images temporarily to disk for DeepFace
    image1_path = "temp_image1.jpg"
    image2_path = "temp_image2.jpg"
    cv2.imwrite(image1_path, cv2.cvtColor(image1_rgb, cv2.COLOR_RGB2BGR))
    cv2.imwrite(image2_path, cv2.cvtColor(image2_rgb, cv2.COLOR_RGB2BGR))

    # Compare the faces using DeepFace
    result = DeepFace.verify(image1_path, image2_path)

    # Check the result
    if result['verified']:
        return "Faces match!"
    else:
        return "Faces do not match!"
    
    
if __name__ == '__main__':
    app.run(debug=True)


