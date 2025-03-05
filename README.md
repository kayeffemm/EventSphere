# EventSphere

EventSphere is a REST API that allows users to track upcoming events for their favorite artists using the Ticketmaster Discovery API. Users can follow artists, view events near them, and save events of interest.

## Features
- User authentication with JWT (Login/Signup)
- Add favorite artists to track their upcoming events
- Fetch event data from Ticketmaster and cache it in the database
- Display events near the user within a 6-month timeframe
- Save events for future reference
- Provide a link to Ticketmaster for ticket purchases

## Tech Stack
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Authentication:** JWT
- **Deployment:** Vercel / Render
- **API Security:** Input sanitization, validation

## Database Schema
The database consists of five main tables:

```dbml
Table users {
  id uuid [primary key]
  name varchar(100)
  email varchar [unique]
  password varchar // Hashed password
  location varchar(100)
  created_at timestamp
}

Table artists {
  id uuid [primary key]
  name varchar(100)
  ticketmaster_id varchar [unique]
  created_at timestamp
}

Table interests {
  id uuid [primary key]
  user_id uuid
  artist_id uuid
  created_at timestamp
}

Table events {
  id uuid [primary key]
  ticketmaster_id varchar [unique]
  artist_id uuid
  name varchar(200)
  date timestamp
  location varchar(200)
  ticket_url varchar
  created_at timestamp
}

Table saved_events {
  id uuid [primary key]
  user_id uuid
  event_id uuid
  created_at timestamp
}

// Relationships
Ref: interests.user_id > users.id
Ref: interests.artist_id > artists.id
Ref: events.artist_id > artists.id
Ref: saved_events.user_id > users.id
Ref: saved_events.event_id > events.id
```

## API Endpoints
### Authentication
- `POST /auth/signup` - Create a new user
- `POST /auth/login` - Login and get a JWT token

### Artists
- `GET /artists` - Get all artists
- `POST /artists` - Add an artist to track

### Events
- `GET /events` - Get upcoming events for tracked artists
- `GET /events/{event_id}` - Get details of a specific event

### User Interests
- `GET /user/interests` - Get user's tracked artists
- `POST /user/interests/{artist_id}` - Follow an artist

### Saved Events
- `GET /user/saved-events` - Get user's saved events
- `POST /user/saved-events/{event_id}` - Save an event

## Setup and Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/eventsphere.git
   cd eventsphere
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```sh
   cp .env.example .env
   ```
   Fill in the required environment variables.

5. Run the database migrations:
   ```sh
   alembic upgrade head
   ```
6. Start the server:
   ```sh
   uvicorn app:main --reload
   ```

## Future Improvements (V2)
- End-to-End Testing
- External Authentication (Cognito, Firebase, Auth0)
- Automated Event Fetching with Cron Jobs
- GitHub Actions for CI/CD
- API Documentation
- Possible direct ticket purchasing

