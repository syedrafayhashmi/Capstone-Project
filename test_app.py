import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import db_drop_and_create_all, setup_db, Movie, Actor, MovieActor
from auth import AuthError, requires_auth

database_name = "database_test.db"
executive_producer_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1EZEdNMFpCTURFeU16WkZNems0UWtFMFJUZzNRak16UkVFMlJqQXdNVVpCT1RKQk5EYzROUSJ9.eyJpc3MiOiJodHRwczovL2lmYXRpbWFoLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTI4ZWI0MGY4ZjU1YTBlYWFhOTVmZjkiLCJhdWQiOiJjYXBzdG9uZSIsImlhdCI6MTU4MDUyNjg0OCwiZXhwIjoxNTgzMTE4ODQ4LCJhenAiOiJmanlKaFd3MDZBTVdUN3MzWnp0cU1GMzhkc0g5dU94cyIsImd0eSI6InBhc3N3b3JkIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9yIiwiZGVsZXRlOm1vdmllIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwb3N0OmFjdG9yIiwicG9zdDptb3ZpZSIsInVwZGF0ZTphY3RvciIsInVwZGF0ZTptb3ZpZSJdfQ.ZDOj8k8nZ0NdmrS-6xU3rBSEAPmqtedHIxI_u4B6Z7TwrisH68lCm_poE3BbSCjtgc0-26g2yxYjXwJBbj1eYGkGfvFxw9W4Aab4L0U3odp3VVBoh8QCHaeXxvXx0aK1sltoZLV-U14STVhd2kaEMigMeeVW1W7set7dFb17KwMfh2yt68ukUusGUCMh34upD2E0-sjFRerXDIjXJfNnrDGS5L4g6BbfTSAwy_dSuajZQaGuCYQU-DKBo0SUhUebAXQTqoUSf2wctq6ttQdRbtYAkCw5E8xgLmtpo_LiJpBkVbluy94qfASQlIUjTcrizAy44btgbfJVYIGiuYOIgQ'}
casting_director_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1EZEdNMFpCTURFeU16WkZNems0UWtFMFJUZzNRak16UkVFMlJqQXdNVVpCT1RKQk5EYzROUSJ9.eyJpc3MiOiJodHRwczovL2lmYXRpbWFoLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTI5MDExZjJmNWNjODBlOTg2Y2ZkOTUiLCJhdWQiOiJjYXBzdG9uZSIsImlhdCI6MTU4MDUzMTUxOSwiZXhwIjoxNTgzMTIzNTE5LCJhenAiOiJmanlKaFd3MDZBTVdUN3MzWnp0cU1GMzhkc0g5dU94cyIsImd0eSI6InBhc3N3b3JkIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9yIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwb3N0OmFjdG9yIiwidXBkYXRlOmFjdG9yIiwidXBkYXRlOm1vdmllIl19.krU8wi3-DOgVeAzPX4jXqsbXTE4XbEc3T5t67nzE56bF3DCJVFLA5nqDxPHCO1iQ6Vph_CWFvsb9WFXhfWIjYhyCq4e4XKuhtNTr3eQwYycweZsWdcQgTnx9PGRwNRUNHi3DKLBYD1M85zmYDpeDzIjjluXKNxLZ855dtQRv22YWkKHuWpQ6Islxdggs_qbbHnV1ojOGYnm5DZDHWhMBV3SPiYqxBJhI1E8PGNf_lNmOqzMOqzzvmvaZIDMLoVkIacruqs72Mo49X0RStNBFAGBboUSQT8mcVlQB0AQywpLvpZYw-LqsgMmKnonA4PhxFsM5sEOL1KsSd-8UydEHsw'}
casting_assistant_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1EZEdNMFpCTURFeU16WkZNems0UWtFMFJUZzNRak16UkVFMlJqQXdNVVpCT1RKQk5EYzROUSJ9.eyJpc3MiOiJodHRwczovL2lmYXRpbWFoLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTM0YzRiM2FhYTFmMDBlNjU1NDkyZjQiLCJhdWQiOiJjYXBzdG9uZSIsImlhdCI6MTU4MDUzMTU3MCwiZXhwIjoxNTgzMTIzNTcwLCJhenAiOiJmanlKaFd3MDZBTVdUN3MzWnp0cU1GMzhkc0g5dU94cyIsImd0eSI6InBhc3N3b3JkIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.eV8f45n2BNon5n7DgtdcUvvlEYguLyhLER7pdNwQi_A_oUogyGEcVTtoMMaJMNYAIInRfD8ovqJ91O33-BfQco6M23FhnydhJkz7xsrEJxB1XuX-fpIhglF1LPh5eTDnRJyTiKH6nmEFBPpDJVYrL5BY-T9LsNZe_2TluczlKh3boDIh0ShV2ekvdJFdQjJxgWVd8_LhOCXS1h8GuIY6LwCLx1vHJN7KZXuUVDTgSz82t_SbH6qOkD7ZKUFFNIlDAPKisYQtjaRUBH-IyMgWTu9PGV-6A-82vTtyy96JN_dt1i3FKKlheYc4dXepH1Odib5ATHCDybqgWd0rzoJU-A'}


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
