# Starting the Frontend

## Quick Start Commands

You're now in the `frontend` directory with all dependencies installed. Here's what to do next:

### 1. Make sure Django backend is running

In a **separate terminal**, activate your Python venv and start Django:

```bash
# Activate venv (if not already active)
.venv\Scripts\activate  # Windows PowerShell
# or
source .venv/Scripts/activate  # Git Bash

# Start Django server
python manage.py runserver
```

The backend should be running at: http://127.0.0.1:8000

### 2. Start Next.js development server

In the **current terminal** (where you ran npm install), run:

```bash
npm run dev
```

You should see:
```
  ▲ Next.js 14.0.4
  - Local:        http://localhost:3000
  ✓ Ready in 2.5s
```

### 3. Access the application

- **Frontend:** http://localhost:3000
- **Backend API:** http://127.0.0.1:8000/api
- **API Docs:** http://127.0.0.1:8000/api/docs/

### 4. Login

- Go to http://localhost:3000
- You'll be redirected to `/login`
- Use your Django superuser credentials (or any user you created)

## Troubleshooting

### Port 3000 already in use?

```bash
# Use a different port
npm run dev -- -p 3001
```

### CORS errors?

Make sure:
1. Django backend is running
2. CORS is configured in Django settings
3. Backend URL matches `.env.local`

### Can't connect to API?

1. Check `.env.local` has correct URL
2. Verify Django is running on port 8000
3. Check browser console for errors

## Next Steps

Once both servers are running:
1. Login to the frontend
2. Explore the dashboard
3. Try creating products
4. Test the POS interface
5. Check notifications

Happy coding! 🚀

