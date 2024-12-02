# GardenConnect 🌱

Welcome to **GardenConnect**, a social media platform for gardening enthusiasts! This project is designed to connect gardening lovers, enabling them to share their knowledge, showcase their gardens, and interact with like-minded individuals.

---

## Features

### User Authentication

- **Register and Login**: Users can securely register and log in to their accounts.
    
- **Password Hashing**: All passwords are stored securely using hashing.
    
- **Session Management**: Routes are protected, requiring authentication to access features.
    

### User Profiles

- **View Profiles**: Each user has a public profile that displays their gardening posts and details.
    
- **Edit Profile**: Users can update their profile details, including bio, location, and profile picture.
    
- **Follow System**: Users can follow/unfollow others and see their followers/following lists.
    

### Posts and Comments

- **Create Posts**: Users can share gardening tips, ideas, or updates by creating posts.
    
- **Commenting System**: Engage with posts by leaving comments. Nested replies are supported for discussions.
    
- **Likes**: Users can like posts and comments, with live updates on like counts.
    

### Protected Routes

- All routes are secure and accessible only to authenticated users. Unauthenticated requests are redirected to the login page.
    

---

## Project Status

**Backend Logic**: The core backend functionality is complete, including:

- User authentication and authorization.
    
- CRUD operations for posts and comments.
    
- Likes and follow system.
    
- Profile updates and public/private profiles.
    

**Frontend Design**: The current design is minimal and functional. I ran out of time to enhance the user interface, but all backend logic and APIs are operational.

Feel free to contribute to the design or implement improvements!

---

## How to Run the Project

1. git clone https://github.com/niamhfoley-dev/assignment_4
    
2. pip install -r requirements.txt

3. docker-compose run to start db container
    
4. flask db upgrade
    
5. flask run
    

---

## Testing

The project includes test cases for the backend to ensure reliability:

- **Authentication Tests**: Test user registration, login, and protected routes.
    
- **Post and Comment Tests**: Verify post creation, updates, and comments.
    
- **Like and Follow System**: Ensure likes and follow functionality work as expected

## Future Enhancements

- **Frontend Design**: Build a more appealing and responsive user interface.
    
- **Advanced Features**: Add support for photo galleries, garden planning tools, and event scheduling.
    

---

Happy gardening! 🌻