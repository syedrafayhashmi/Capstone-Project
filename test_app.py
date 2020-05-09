import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import db_drop_and_create_all, setup_db, Movie, Actor, MovieActor
from auth import AuthError, requires_auth

database_name = "database_test.db"
executive_producer_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjBFMXlNNWltTXAxQWtPN21tYzEyeSJ9.eyJpc3MiOiJodHRwczovL3N5ZWQtcmFmYXkuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlYjRmZDQ0NmI2OWJjMGMxMjAyMzRkNSIsImF1ZCI6ImFwaSIsImlhdCI6MTU4OTAyNDg2NCwiZXhwIjoxNTg5MDMyMDY0LCJhenAiOiJUM2lyZ1E4Z0Z3YjhncXlFblo0alNMV0E0NGJYTmFFVSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9yIiwiZGVsZXRlOm1vdmllIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwb3N0OmFjdG9yIiwicG9zdDptb3ZpZSIsInVwZGF0ZTphY3RvciIsInVwZGF0ZTptb3ZpZSJdfQ.YKBVSY3FTYAfXSyvhq-NemKH57I-GWFJNOJ371cS9YJ3JbE7KoO70pn6BOQm2dH9f5x6U919a-EDgbDEKxn0ONNR68iGWR9H8m8XDwAOd9sYTPveuhMopiBuiVEy8yJmYO0nrSascLDwh3EtN9MgU1wifi9bXsjw6xpFusc40bqNEmONlMwjlpp0zVtE0BJ4yb25ajarC8KyzdiVTKM46wRZggGIo2O7FyPCraRbY7fIjXOI6__DMfJwN30HUTQ0a0lvyclaOimkvDYNdWuaVAMaENx_iE90EAS3tE-mPwBzjce5m85XvxCu5vRHgaZ4UyKWllEImZLjuFIjMa5WKg'}
casting_director_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjBFMXlNNWltTXAxQWtPN21tYzEyeSJ9.eyJpc3MiOiJodHRwczovL3N5ZWQtcmFmYXkuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlYjUwNDBiMWNjMWFjMGMxNDkyYzUwZiIsImF1ZCI6ImFwaSIsImlhdCI6MTU4OTAyNDk3NiwiZXhwIjoxNTg5MDMyMTc2LCJhenAiOiJUM2lyZ1E4Z0Z3YjhncXlFblo0alNMV0E0NGJYTmFFVSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9yIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwb3N0OmFjdG9yIiwidXBkYXRlOmFjdG9yIiwidXBkYXRlOm1vdmllIl19.C2vSMcpE8ck6rTll6Lkv_qf57PMZx1exRiF9YWnrcc8SsuVq3OUNX8HwF2UzVK0bWm2Aw7skuNUNOi61fivqvAawkODoMHunRtJjZP3FPH75Y4izaVyWK_T_UUsicY67eHgy5UoXGm7XZecJ4VRpnAX0DXB58CQJRPPPuFF9_G3lG1tAsdoc5VKI0ZD9YRHtOWCt_Etr4KXoEi_SV3k_49PqrqH0Lj8K5Ji3Q9oNE0hFT2o2wEpxiBUZLLJjTEJ4wwNvblrjciK34XtzFmKuKF0mHe4NxdURFuUzeGyqasypiqUWsbWJmYRDKH4HImsOIhTFYmC0LxMUJULwyfjFzg'}
casting_assistant_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjBFMXlNNWltTXAxQWtPN21tYzEyeSJ9.eyJpc3MiOiJodHRwczovL3N5ZWQtcmFmYXkuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlYjUwMzQwNTRiMTRjMGMxMjg0MTVhMCIsImF1ZCI6ImFwaSIsImlhdCI6MTU4OTAyNTA2MCwiZXhwIjoxNTg5MDMyMjYwLCJhenAiOiJUM2lyZ1E4Z0Z3YjhncXlFblo0alNMV0E0NGJYTmFFVSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.h6zoLdKqqzMiVQcY05E3ZrDAHA4X7lx6WEn9vq1KicstnTqq7MPZIcfl_6OA616giqpKEncNG0Ta2mQD8E6BDncbSMS8PVXCeKXG8-66JqccTE3a4dDXBrtdIhh_CBYlJB505Yh1u5V0iAloMdpISpvut5zWizOfw3af2rsFWqPhOE8_ZN-_zGx_8XmI-wwwpPwKhiG72xuvyRnf9mJQVbvn-z5YHON6emfDlgL87f5g58soySwpjqNTfLtuemvMiKAjSSZNIdziTmhIju8-w4fUBPGtRn62grRRQxo1QSBcrqahzFWIan58zXI3RfvEkP8EdtZq37kY4Vnlno2tTA'}


class CapstoneTestCase(unittest.TestCase):
    """This class represents the Capstone test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(None, database_name)
        self.client = self.app.test_client
        setup_db(self.app, "database_test.db")

        self.new_movie = {
            'title': 'Movie1',
            'release_date': '2020-03-29'
        }

        self.new_actor = {
            'name': 'Actor',
            'age': 20,
            'gender': 'Female'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
        # db_drop_and_create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    4 Tests Cases for the get_movies
    The first test for the expected behavior
    when the UserRole is executive_producer
    The second test for handling one kind of error
    (405: method_not_allowed)
    The third test for the expected behavior
    when the UserRole is casting_director
    The fourth tests for the expected behavior
    when the UserRole is casting_assistant
    """
    def test_get_movies(self):
        res = self.client().get('/movies', headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_get_movies_method_not_allowed(self):
        res = self.client().get('/movies/1',
                                headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

    def test_get_movies_casting_director(self):
        res = self.client().get('/movies',
                                headers=casting_director_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_get_movies_casting_assistant(self):
        res = self.client().get('/movies', headers=casting_assistant_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)

    """
    4 Tests Cases for the create_movie when the UserRole is executive_producer
    The first test for the expected behavior
    The second test for handling one kind of error (405: method_not_allowed)
    The third test for the expected behavior
    when the UserRole is casting_director
    The fourth tests for the expected behavior
    when the UserRole is casting_assistant
    """
    def test_create_movie(self):
        res = self.client().post('/movies', json=self.new_movie,
                                 headers=executive_producer_headers)
        # Create another movie to be deleted later
        res = self.client().post('/movies', json=self.new_movie,
                                 headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_if_movie_creation_not_allowed(self):
        res = self.client().post('/movies/1', json=self.new_movie,
                                 headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

    def test_create_movie_casting_director(self):
        res = self.client().post('/movies', json=self.new_movie,
                                 headers=casting_director_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_create_movie_casting_assistant(self):
        res = self.client().post('/movies', json=self.new_movie,
                                 headers=casting_assistant_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    """
    2 Tests Cases for the create_movie when the UserRole is executive_producer
    The first test for the expected behavior
    The second test for handling one kind of error
    (422: request unprocessable - when the movie_id is not exist)
    NOTE: the error code for second TestCase could be 404: Not Found as well
    """
    def test_update_movie(self):
        mv = Movie.query.first()
        res = self.client().patch('/movies/'+str(mv.id), json=self.new_movie,
                                  headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_update_movies_if_not_exist(self):
        res = self.client().patch('/movies/20000', json=self.new_movie,
                                  headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    """
    2 Tests Cases for the delete_movie when the UserRole is executive_producer
    The first test for the expected behavior
    The second test for handling one kind of error
    (422: request unprocessable - when the movie_id is not exist)
    NOTE: the error code for second TestCase could be 404: Not Found as well
    """

    def test_delete_movies(self):
        mv = Movie.query.first()
        res = self.client().delete('/movies/'+str(mv.id),
                                   headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_movies_if_not_exist(self):
        res = self.client().delete('/movies/2000',
                                   headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    """
    2 Tests Cases for the get_actors when the UserRole is executive_producer
    The first test for the expected behavior
    The second test for handling one kind of error (405: method_not_allowed)
    """
    def test_get_actors(self):
        res = self.client().get('/actors', headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_get_actors_method_not_allowed(self):
        res = self.client().get('/actors/1',
                                headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

    """
    4 Tests Cases for the create_actor when the UserRole is executive_producer
    The first test for the expected behavior
    The second test for handling one kind of error (405: method_not_allowed)
    The third test for the expected behavior
    when the UserRole is casting_director
    The fourth tests for the expected behavior
    when the UserRole is casting_assistant
    """
    def test_create_actor(self):
        res = self.client().post('/actors', json=self.new_actor,
                                 headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_if_actor_creation_not_allowed(self):
        res = self.client().post('/actors/1', json=self.new_actor,
                                 headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

    def test_create_actor_casting_director(self):
        res = self.client().post('/actors', json=self.new_actor,
                                 headers=casting_director_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_create_actor_casting_assistant(self):
        res = self.client().post('/actors', json=self.new_actor,
                                 headers=casting_assistant_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    """
    2 Tests Cases for the create_actor when the UserRole is executive_producer
    The first test for the expected behavior
    The second test for handling one kind of error
    (422: request unprocessable - when the actor_id is not exist)
    NOTE: the error code for second TestCase could be 404: Not Found as well
    """
    def test_update_actor(self):
        ac = Actor.query.first()
        res = self.client().patch('/actors/'+str(ac.id), json=self.new_actor,
                                  headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_update_actors_if_not_exist(self):
        res = self.client().patch('/actors/20000', json=self.new_actor,
                                  headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    """
    2 Tests Cases for the delete_actor when the UserRole is executive_producer
    The first test for the expected behavior
    The second test for handling one kind of error
    (422: request unprocessable - when the actor_id is not exist)
    NOTE: the error code for second TestCase could be 404: Not Found as well
    """

    def test_delete_actors(self):
        ac = Actor.query.first()
        res = self.client().delete('/actors/'+str(ac.id),
                                   headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_actors_if_not_exist(self):
        res = self.client().delete('/actors/2000',
                                   headers=executive_producer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
