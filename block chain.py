[3:30 PM, 1/10/2024] Balu: import hashlib
from flask import Flask, render_template, request, url_for, redirect, flash, session
import pandas as pd
import numpy as np
from mysql import connector
import mysql.connector
from flask_mail import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine

def get_db():
    mydb=mysql.connector.connect(user='root',password='',port=3306,database='ehealthsystems')
    cur=mydb.cursor()
    return mydb,cur

app=Flask(_name_)
app.secret_key="kjabcnsnc89yr84rfwe7ry"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/userreg",methods=["POST","GET"])
def userreg():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        age=request.form['age']
        number=request.form['number']
        password=request.form['password']
        confirmpassword=request.form['confirmpassword']
        if password == confirmpassword:
            mydb,cur=get_db()
            sql="select * from userregistration where Email='%s'"%(email)
            cur.execute(sql)
            data=cur.fetchall()
            mydb.commit()
            mydb.close()
            if data == []:
                pri_key=randint(000000,999999)
                mydb,cur=get_db()
                sql="insert into userregistration(Name,Email,Age,Number,Password,Prikey)values(%s,%s,%s,%s,%s,%s)"
                val=(name,email,age,number,password,pri_key)
                cur.execute(sql,val)
                mydb.commit()
                mydb.close()
                content = f"The key to login :key 1 : {pri_key}"
                sender_address = 'alurusasidhar2804@gmail.com'
                sender_pass = 'fqvwypetwzzydeck'
                receiver_address = email
                message = MIMEMultipart()
                message['From'] = sender_address
                message['To'] = receiver_address
                message['Subject'] = 'Blockchain for Secure EHRs Sharing of Mobile Cloud Based E-Health Systems'
                message.attach(MIMEText(content, 'plain'))
                section = smtplib.SMTP('smtp.gmail.com', 587)
                section.starttls()
                section.login(sender_address, sender_pass)
                text = message.as_string()
                section.sendmail(sender_address, receiver_address, text)
                section.quit()
                return render_template("userlog.html")
            else:
                msg="Registartion successfully"
                return render_template('userreg.html',msg=msg)
    return render_template('userreg.html')

@app.route("/userlog",methods=['POST','GET'])
def userlog():
    if request.method=='POST':
        email=request.form['email']
        session['useremail']=email
        password=request.form['password']
        OTP=request.form['key']
        mydb,cur=get_db()
        sql="select * from userregistration Where Email='%s' and Password='%s'"%(email,password)
        cur.execute(sql)
        data=cur.fetchall()
        mydb.commit()
        mydb.close()
        if data==[]:
            msg = "details are not valid"
            return render_template("userlog.html", msg=msg)
        else:
            if OTP == data[0][-1]:
                return render_template("userhome.html")
            else:
                msg="OTP is not valid"
                return render_template("userlog.html",msg=msg)
    return render_template("userlog.html")

@app.route('/cloudlogin',methods=['POST','GET'])
def cloudlogin():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        if email=="cloud@gmail.com" and password=='cloud':
            return render_template("cloudhome.html")
        else:
            msg="details are not valid"
            return render_template("cloudlogin.html",msg=msg)
    return render_template("cloudlogin.html")


@app.route("/uploadfile",methods=['POST','GET'])
def uploadfile():
    global x
    if request.method=='POST':
        filedata=request.files['filedata']
        filename=filedata.filename
        session['filename']=filename
        data=pd.read_csv(filedata)
        x=data
        return render_template("uploadfile.html",data=x)
    return render_template("uploadfile.html")

@app.route("/viewrecords")
def viewrecords():
    df=x
    mydb,cur=get_db()
    sql = "TRUNCATE table filedata"
    cur = mydb.cursor()
    cur.execute(sql)
    mydb.commit()
    mydb.close()
    engine = create_engine("mysql://{user}:{pw}@localhost:{port}/{db}".format(user="root", pw="",port=3306, db="ehealthsystems"))
    df.to_sql('filedata', con=engine, if_exists='append', chunksize=150,index=False)

    mydb,cur=get_db()
    sql="select * from filedata"
    data=pd.read_sql_query(sql,mydb)
    return render_template('viewrecords.html',cols=data.columns.values,rows=data.values.tolist())

@app.route('/encryptfiles')
def encryptfiles():
    mydb,cur=get_db()
    sql="select * from filedata"
    data=pd.read_sql_query(sql,mydb)
    for i in range(len(data)):
        i=data.values[i]
        age = str(i[1])
        sex=str(i[2])
        cp=str(i[3])
        trestbps=str(i[4])
        chol=str(i[5])
        fbs=str(i[6])
        restecg=str(i[7])
        thalach=str(i[8])
        exang=str(i[9])
        oldpeack=str(i[10])
        slope=str(i[11])
        ca=str(i[12])
        thal=str(i[13])
        target=str(i[14])
        pid=(i[15])
        mydb,cur=get_db()
        sql="insert into filedata_encdata(age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,target,Generatedkey,useremail)values(AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),AES_ENCRYPT(%s,'keys'),%s,%s)"
        val = (age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeack, slope, ca, thal, target,pid,session['useremail'])
        cur.execute(sql,val)
        mydb.commit()
        mydb.close()
    return render_template('encryptfiles.html')


@app.route('/Viewencrecords')
def Viewencrecords():
    mydb,cur=get_db()
    sql="select age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target,Generatedkey from filedata_encdata where useremail='%s'"%(session['useremail'])
    data=pd.read_sql_query(sql,mydb)
    return render_template("Viewencrecords.html",cols=data.columns.values,rows=data.values.tolist())

@app.route('/viewresponse')
def viewresponse():
    mydb,cur=get_db()
    sql="select distinct Status from filedata_encdata where useremail='%s'"%(session['useremail'])
    cur.execute(sql)
    data=cur.fetchall()
    mydb.commit()
    mydb.close()
    status=data[0][0]
    if status == 'accept':
        flash("permission granted","success")
        return render_template('viewresponse.html')
    else:
        try:
            flash("permission in not granted", "success")
            msg="notaccepted"
            return render_template('viewresponse.html',msg=msg)
        except:
            pass
    return render_template('viewresponse.html')

@app.route('/blockchain')
def blockchain():
    mydb,cur=get_db()
    sql="select Generatedkey from filedata_encdata where useremail='%s'"%(session['useremail'])
    cur.execute(sql)
    data=cur.fetchall()
    mydb.commit()
    mydb.close()
    return render_template('blockchain.html',data=data)

@app.route('/uploadtocloudserver')
def uploadtocloudserver():
    mydb,cur=get_db()
    sql="update filedata_encdata set status='done' where status='accept' and useremail='%s'"%(session['useremail'])
    cur.execute(sql)
    mydb.commit()
    mydb.close()
    flash("request sent successfully",'success')
    return redirect('blockchain')

@app.route('/sendrequest')
def sendrequest():
    mydb,cur=get_db()
    sql="update filedata_encdata set status='pending' where status='none' and useremail='%s'"%(session['useremail'])
    cur.execute(sql)
    mydb.commit()
    mydb.close()
    flash("request sent successfuly","success")
    return redirect(url_for('Viewencrecords'))


@app.route('/usersrequest')
def usersrequest():
    mydb,cur=get_db()
    sql="select distinct useremail from filedata_encdata where status='pending'"
    data=pd.read_sql_query(sql,mydb)
    return render_template('usersrequest.html',cols=data.columns.values,rows=data.values.tolist())

@app.route('/downloadrequest')
def downloadrequest():
    return render_template('downloadrequest.html')

@app.route('/filesearch', methods=['POST', 'GET'])
def filesearch():
    if request.method == 'POST':
        fileid = request.form['searchfile']
        mydb, cur = get_db()
        sql = "SELECT status FROM filedata_encdata WHERE Generatedkey='%s' AND useremail='%s'" % (fileid, session['useremail'])
        cur.execute(sql)
        data = cur.fetchall()
        mydb.commit()
        mydb.close()
        if data[0][0]==[]:
            msg="please raise request"
            return render_template('downloadrequest.html', msg=msg)
        elif data[0][0]=='done':
            mydb,cur=get_db()
            sql = "update filedata_encdata set status='request' where status='accept' and useremail='%s' and Generatedkey='%s'" % (session['useremail'],fileid)
            cur.execute(sql)
            mydb.commit()
            mydb.close()
            msg="file not found"
            msg1="your request sent to cloud"
            return render_template('downloadrequest.html',msg=msg,msg1=msg1)
        elif data[0][0]=='complete':
            mydb,cur=get_db()
            sql="select Slno,age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,target from filedata_encdata where useremail='%s' and Generatedkey='%s'" % (session['useremail'],fileid)
            data=pd.read_sql_query(sql,mydb)
            msg = "your request accepted"
            return render_template('downloadrequest.html', msg=msg,cols=data.columns.values,rows=data.values.tolist())
        else:
            msg = "request already sent"
            return render_template('downloadrequest.html', msg=msg)
    return render_template('downloadrequest.html')

@app.route('/decryptfile/<z>')
def decryptfile(z=0):
    mydb,cur=get_db()
    sql="select AES_DECRYPT(age,'keys'),AES_DECRYPT(sex,'keys'),AES_DECRYPT(cp,'keys'),AES_DECRYPT(trestbps,'keys'),AES_DECRYPT(chol,'keys'),AES_DECRYPT(fbs,'keys'),AES_DECRYPT(restecg,'keys'),AES_DECRYPT(thalach,'keys'),AES_DECRYPT(exang,'keys'),AES_DECRYPT(oldpeak,'keys'),AES_DECRYPT(slope,'keys'),AES_DECRYPT(ca,'keys'),AES_DECRYPT(thal,'keys'),AES_DECRYPT(target,'keys') from filedata_encdata where Slno='%s'"%(z)
    cur.execute(sql)
    data=cur.fetchall()
    mydb.commit()
    mydb.close()
    j=[j for i in data for j in i]
    f=[k.decode() for k in j]
    a=f[0]
    b=f[1]
    c=f[2]
    d=f[3]
    e=f[4]
    g=f[5]
    h=f[6]
    i=f[7]
    j=f[8]
    k=f[9]
    l=f[10]
    m=f[11]
    n=f[12]
    o=f[13]
    return render_template('decryptfile.html',a=a,b=b,c=c,d=d,e=e,g=g,h=h,i=i,j=j,k=k,l=l,m=m,n=n,o=o)

@app.route('/downloadfilerequest')
def downloadfilerequest():
    mydb,cur=get_db()
    sql="select distinct useremail from filedata_encdata where status='done'"
    data=pd.read_sql_query(sql,mydb)
    return render_template('downloadfilerequest.html',cols=data.columns.values,rows=data.values.tolist())

@app.route('/verifyfiles/<c>/')
def verifyfiles(c=''):
    mydb,cur=get_db()
    sql="update filedata_encdata set status='complete' where useremail='%s'"%(c)
    cur.execute(sql)
    mydb.commit()
    mydb.close()
    return redirect(url_for('downloadfilerequest'))

@app.route('/downloadfile')
def downloadfile():
    return redirect(url_for('downloadrequest'))


# viewallrecords
@app.route('/viewallrecords')
def viewallrecords():
    mydb,cur=get_db()
    sql="select * from filedata"
    data=pd.read_sql_query(sql,mydb)
    mydb,cur=get_db()
    sql1="select age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,target from filedata_encdata where status='done' and useremail='%s'"%(session['useremail'])
    data1=pd.read_sql(sql1,mydb)
    return render_template('viewallrecords.html',cols=data.columns.values,rows=data.values.tolist(),cols1=data1.columns.values,rows1=data1.values.tolist())

@app.route('/acceptuserrequest/<n1>')
def acceptuserrequest(n1=""):
    mydb,cur=get_db()
    sql="update filedata_encdata set Status='accept' where useremail='%s' and Status='pending'"%(n1)
    cur.execute(sql)
    mydb.commit()
    mydb.close()
    mydb,cur=get_db()
    sql="select Email from userregistration where Id='%s'"%(n1)
    cur.execute(sql)
    data=cur.fetchall()
    mydb.commit()
    mydb.close()
    content = f"Your request is accepted "
    sender_address = 'a4@gmail.com'
    sender_pass = 'fqvetwzzydeck'
    receiver_address = n1
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Blockchain for Secure EHRs Sharing of Mobile Cloud Based E-Health Systems'
    message.attach(MIMEText(content, 'plain'))
    section = smtplib.SMTP('smtp.gmail.com', 587)
    section.starttls()
    section.login(sender_address, sender_pass)
    text = message.as_string()
    section.sendmail(sender_address, receiver_address, text)
    section.quit()
    return redirect(url_for('usersrequest'))



@app.route('/securefile/<r1>/<r2>')
def securefile(r1=0,r2=''):
    mydb,cur=get_db()
    sql="select Filedata from dataowneruploadfiles where Slno='%s'"%(r1)
    cur.execute(sql)
    data=cur.fetchall()
    mydb.commit()
    mydb.close()
    enc_data=data[0][0]
    datalen = int(len(enc_data) / 2)
    g = 0
    a = ''
    b = ''
    c = ''
    for i in range(0, 2):
        if i == 0:
            a = enc_data[g: datalen:1]
            result = hashlib.sha1(a.encode())
            hash1 = result.hexdigest()
    c = enc_data[datalen: len(enc_data):1]
    result = hashlib.sha1(c.encode())
    hash2 = result.hexdigest()
    mydb,cur=get_db()
    sql="update dataowneruploadfiles set FileEncData=AES_ENCRYPT('%s','key'),Dataone=AES_ENCRYPT('%s','key'),Datatwo=AES_ENCRYPT('%s','key'),status='allow',Hash1='%s',Hash2='%s' where Slno='%s' and status='accepted'"%(enc_data,a,c,hash1,hash2,r1)
    cur.execute(sql)
    mydb.commit()
    mydb.close()


@app.route("/hsplogout")
def hsplogout():
    return redirect(url_for('home'))


@app.route("/cloudlogout")
def cloudlogout():
    return redirect(url_for('home'))


if _name=="main_":
    app.run(debug=True,port=8000)
[3:30 PM, 1/10/2024] Balu: package com.example.audoptik;

import android.graphics.Bitmap;
import android.graphics.Bitmap.Config;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.Paint.Style;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.media.ImageReader.OnImageAvailableListener;
import android.util.Size;
import android.util.TypedValue;
import android.widget.Toast;

import com.example.audoptik.env.BorderedText;
import com.example.audoptik.env.ImageUtils;
import com.example.audoptik.env.Logger;
import com.example.audoptik.tracking.MultiBoxTracker;

import java.io.IOException;
import java.util.LinkedList;
import java.util.List;

public class DetectorActivity extends CameraActivity implements OnImageAvailableListener {

  private static final Logger LOGGER = new Logger();
  private static final int TF_OD_API_INPUT_SIZE = 300;
  private static final String TF_OD_API_MODEL_FILE =
      "file:///android_asset/ssd_mobilenet_v1_android_export.pb";
  private static final String TF_OD_API_LABELS_FILE = "file:///android_asset/coco_labels_list.txt";

  // Minimum detection confidence to track a detection.
  private static final float MINIMUM_CONFIDENCE_TF_OD_API = 0.6f;

  private static final Size DESIRED_PREVIEW_SIZE = new Size(640, 480);

  private static final float TEXT_SIZE_DIP = 10;

  private Integer sensorOrientation;

  private Classifier detector;

  private Bitmap rgbFrameBitmap = null;
  private Bitmap croppedBitmap = null;
  private Bitmap cropCopyBitmap = null;

  private boolean computingDetection = false;

  private long timestamp = 0;

  private Matrix frameToCropTransform;
  private Matrix cropToFrameTransform;

  private MultiBoxTracker tracker;
  private byte[] luminanceCopy;

  private BorderedText borderedText;

  @Override
  public void onPreviewSizeChosen(final Size size, final int rotation) {
    final float textSizePx =
        TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP, TEXT_SIZE_DIP, getResources().getDisplayMetrics());
    borderedText = new BorderedText(textSizePx);
    borderedText.setTypeface(Typeface.MONOSPACE);

    tracker = new MultiBoxTracker(this);

    int cropSize = TF_OD_API_INPUT_SIZE;

    try {
      detector = TensorFlowObjectDetectionAPIModel.create(
          getAssets(), TF_OD_API_MODEL_FILE, TF_OD_API_LABELS_FILE, TF_OD_API_INPUT_SIZE);
      cropSize = TF_OD_API_INPUT_SIZE;
    } catch (final IOException e) {
      LOGGER.e("Exception initializing classifier!", e);
      Toast toast =
          Toast.makeText(
              getApplicationContext(), "Classifier could not be initialized", Toast.LENGTH_SHORT);
      toast.show();
      finish();
    }

    previewWidth = size.getWidth();
    previewHeight = size.getHeight();

    sensorOrientation = rotation - getScreenOrientation();
    LOGGER.i("Camera orientation relative to screen canvas: %d", sensorOrientation);

    LOGGER.i("Initializing at size %dx%d", previewWidth, previewHeight);
    rgbFrameBitmap = Bitmap.createBitmap(previewWidth, previewHeight, Config.ARGB_8888);
    croppedBitmap = Bitmap.createBitmap(cropSize, cropSize, Config.ARGB_8888);

    frameToCropTransform =
        ImageUtils.getTransformationMatrix(
            previewWidth, previewHeight,
            cropSize, cropSize,
            sensorOrientation, false);

    cropToFrameTransform = new Matrix();
    frameToCropTransform.invert(cropToFrameTransform);

    trackingOverlay = findViewById(R.id.tracking_overlay);

    trackingOverlay.addCallback(
        new OverlayView.DrawCallback() {
          @Override
          public void drawCallback(final Canvas canvas) {
            tracker.draw(canvas);
          }
        });
  }

  OverlayView trackingOverlay;

  @Override
  protected void processImage() {
    ++timestamp;
    final long currTimestamp = timestamp;
    byte[] originalLuminance = getLuminance();
    tracker.onFrame(
        previewWidth,
        previewHeight,
        sensorOrientation);
    trackingOverlay.postInvalidate();

    // No mutex needed as this method is not reentrant.
    if (computingDetection) {
      readyForNextImage();
      return;
    }
    computingDetection = true;
    LOGGER.i("Preparing image " + currTimestamp + " for detection in bg thread.");

    rgbFrameBitmap.setPixels(getRgbBytes(), 0, previewWidth, 0, 0, previewWidth, previewHeight);

    if (luminanceCopy == null) {
      luminanceCopy = new byte[originalLuminance.length];
    }
    System.arraycopy(originalLuminance, 0, luminanceCopy, 0, originalLuminance.length);
    readyForNextImage();

    final Canvas canvas = new Canvas(croppedBitmap);
    canvas.drawBitmap(rgbFrameBitmap, frameToCropTransform, null);

    runInBackground(
        new Runnable() {
          @Override
          public void run() {
            LOGGER.i("Running detection on image " + currTimestamp);
            final List<Classifier.Recognition> results = detector.recognizeImage(croppedBitmap);

            cropCopyBitmap = Bitmap.createBitmap(croppedBitmap);
            final Canvas canvas = new Canvas(cropCopyBitmap);
            final Paint paint = new Paint();
            paint.setColor(Color.RED);
            paint.setStyle(Style.STROKE);
            paint.setStrokeWidth(2.0f);

              final List<Classifier.Recognition> mappedRecognitions =
                    new LinkedList<>();

            for (final Classifier.Recognition result : results) {
              final RectF location = result.getLocation();
              if (location != null && result.getConfidence() >= MINIMUM_CONFIDENCE_TF_OD_API) {
                LOGGER.i("Title: " + result.getTitle());
                canvas.drawRect(location, paint);

                cropToFrameTransform.mapRect(location);
                result.setLocation(location);
                mappedRecognitions.add(result);
              }
            }

            tracker.trackResults(mappedRecognitions);

            toSpeech(mappedRecognitions);
            trackingOverlay.postInvalidate();

            computingDetection = false;
          }
        });
  }



  @Override
  protected int getLayoutId() {
    return R.layout.camera_connection_fragment_tracking;
  }

  @Override
  protected Size getDesiredPreviewFrameSize() {
    return DESIRED_PREVIEW_SIZE;
  }

}