# GitPulse Web Application

This is the web interface for GitPulse, a tool for analyzing Git repositories and understanding contributor impact.

## Features

- **Repository Analysis**: Analyze any GitHub repository to understand contributor statistics
- **Contributor Insights**: View detailed information about each contributor's impact
- **Language Distribution**: See the programming languages used in the repository
- **Contribution Impact**: Visualize the impact of top contributors
- **Search Functionality**: Filter contributors by name or email

## Running the Web Application

To run the GitPulse web application:

```bash
# From the project root
python -m gitpulse.web.run
```

This will start the web server at http://localhost:8000

## API Endpoints

The web application exposes the following API endpoints:

- `POST /analyze`: Analyze a Git repository and return contributor statistics
- `POST /languages`: Get language distribution in the repository
- `GET /health`: Health check endpoint

## Technologies Used

- **Backend**: FastAPI, Python
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: TailwindCSS
- **Charts**: Chart.js
- **Icons**: Font Awesome

## Design

The web interface is inspired by GitHub's design language, using similar colors and UI patterns to provide a familiar experience for users who are already comfortable with GitHub.

## Screenshots

![GitPulse Web Interface](static/img/screenshot.png)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 