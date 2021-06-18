from flask import Blueprint, session, request, jsonify, abort
from functools import wraps
from flaskapp import db, api, pagination
from flask_login import current_user
from flask_restful import Resource
from flaskapp.routes import *


from flaskapp.models import *

class RateAPI(Resource):
        
    @token_required
    def get(self, id=None):
        message = ""
        if(id):
            rate = Rating.query.filter_by(id=id)
            rating = rate.first()
            if(rating):
                if(is_student(request) and not(rating.rates.student_id == get_current_user(request)['id'])) or (is_teacher(request) and not(rating.rates.teachers_id == get_current_user(request)['id'])):
                    return abort(400, {'message': "Access denied"}) 
                return pagination.paginate(rate, rating_fields)
            else:
                message = "Rating not found"
        else:
                if(is_student(request)):
                    ratings = Rating.query.join(Work, Work.student_id == get_current_user(request)['id'])
                elif(is_teacher(request)):
                    ratings = Rating.query.join(Work, Work.teachers_id == get_current_user(request)['id'])
                else:
                    ratings = Rating.query.all()
                if(ratings):
                    return pagination.paginate(ratings, rating_fields)
                else:
                    message = "Ratings not available"

       
        return abort(400, {'message': message})

    def post(self):
        message = ""
        if(is_teacher(request) or is_company(request)):
            data = request.form
            if(data and data.get('work_id')  
                and data.get('review')):
                
                try:
                    rating = Rating.query.filter_by(work_id=data['work_id']).first()
                    work = Work.query.filter_by(id=data['work_id']).first()
                    if(rating  and is_company(request)):
                        if(work.done.company_id == get_current_user(request)['id']):
                            if(rating.company_review):
                                message = "Already reviewed"
                            else:
                                rating.company_review = data['review']
                                db.session.commit() 
                                return "Reviewed successfully" 
                        else:
                            return abort(400, {'message': "Access denied"})     
                    elif(rating and is_teacher(request) ):
                        if(work.teachers_id == get_current_user(request)['id']):
                            if(rating.teacher_review):
                                message = "Already reviewed"
                            else:
                                rating.teacher_review = data['review']
                                db.session.commit() 
                                return "Reviewed successfully" 
                        else:
                            return abort(400, {'message': "Access denied"})     
                    elif(is_company(request)):
                        if(work.done.company_id == get_current_user(request)['id']):
                            new_rating = Rating(work_id=data['work_id'], 
                                company_review=data['review']) 
                            db.session.add(new_rating) 
                            db.session.commit() 
                            return "Reviewed successfully" 
                        else:
                            return abort(400, {'message': "Access denied"})  
                    elif(is_teacher(request)):
                        if(work.teachers_id == get_current_user(request)['id']):
                            new_rating = Rating(work_id=data['work_id'], 
                                teacher_review=data['review']) 
                            db.session.add(new_rating) 
                            db.session.commit() 
                            return "Reviewed successfully" 
                        else:
                            return abort(400, {'message': "Access denied"})  
                    
                except:
                    message = "Work not created"
            else: 
                message += "Form is missing"

        else:
            message = "Access Denied"
        
        return abort(400, {'message': message})

