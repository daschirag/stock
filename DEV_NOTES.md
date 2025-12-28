# Development Notes & Known Issues

## Current State (v1.0.0)

Last Updated: 2025-12-28

### ✅ What Works

**Backend:**
- FastAPI server starts successfully
- All API endpoints functional
- Mock data generation (no API keys needed)
- Database schema with TimescaleDB
- WebSocket connections
- Background task scheduling
- Logging and error handling

**Frontend:**
- Next.js 15 app renders
- Dashboard loads
- Charts display (using mock data)
- Dark theme active
- Responsive layout

**Integration:**
- Backend ↔ Database communication
- API documentation at `/docs`
- CORS properly configured
- Docker Compose orchestration

### ⚠️ Known Limitations

**ML Models:**
- Models defined but not pre-trained
- First prediction will use moving average fallback
- Training requires sufficient historical data (60+ days)
- GPU support not configured (CPU only)

**Data Pipeline:**
- Real API integration needs API keys
- Background tasks functional but use mock data by default
- VMD decomposition untested with real data

**Frontend:**
- WebSocket integration defined but not fully connected
- Charts use mock data only
- Some pages incomplete (historical analysis, technical indicators detail)
- State management (Zustand) not implemented

**Testing:**
- Integration tests present but may need database
- No end-to-end tests yet
- Performance testing not done

### 🔧 Areas for Improvement

**Priority 1 - Critical for Production:**
1. **Model Training**
   - Train models on real historical data
   - Save trained model weights
   - Model versioning system
   - Retraining automation

2. **Real Data Integration**
   - Get API keys (FRED, NewsAPI)
   - Test with real data
   - Validate data quality
   - Error handling for API limits

3. **Frontend-Backend Connection**
   - Complete WebSocket integration
   - Add state management
   - Error boundary components
   - Loading states

**Priority 2 - Enhanced Features:**
1. **Additional Pages**
   - Historical analysis with prediction vs actual
   - Detailed technical indicators page
   - Model performance metrics
   - Admin dashboard

2. **Caching Layer**
   - Redis for API responses
   - Cache invalidation strategy
   - Prediction caching

3. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - API usage tracking
   - Error rate monitoring

**Priority 3 - Nice to Have:**
1. **User Features**
   - Multiple symbol support (Brent, Dubai, WCS)
   - Custom alert thresholds
   - Export predictions to CSV
   - Dark/light mode toggle

2. **Performance**
   - database query optimization
   - Frontend code splitting
   - Image optimization
   - Lazy loading

3. **Security**
   - Rate limiting
   - API authentication
   - Input sanitization review
   - Security headers

### 🐛 Bugs to Fix

**Backend:**
- [ ] Background task error handling could be improved
- [ ] Prediction service needs trained models for real predictions
- [ ] VMD service fallback may not work with all data shapes

**Frontend:**
- [ ] Chart time range selector not functional
- [ ] Sentiment gauge hardcoded value
- [ ] Real-time price updates not working yet
- [ ] Mobile responsiveness needs testing

**Database:**
- [ ] No data retention policy
- [ ] Missing indexes for some queries
- [ ] Hypertable compression not configured

### 📝 Testing Checklist

Before considering production-ready:

**Backend:**
- [ ] All endpoints return correct status codes
- [ ] Error handling works for invalid inputs
- [ ] Database queries optimized
- [ ] Background tasks don't crash on errors
- [ ] WebSocket handles disconnections gracefully
- [ ] Predictions accuracy validated
- [ ] API rate limiting tested

**Frontend:**
- [ ] All pages load without errors
- [ ] Charts display correctly
- [ ] WebSocket updates work
- [ ] Mobile responsive
- [ ] Error states display properly
- [ ] Loading states smooth
- [ ] Browser compatibility (Chrome, Firefox, Safari)

**Integration:**
- [ ] Full flow: fetch data → process → train → predict works
- [ ] Real API keys tested
- [ ] Docker deployment verified
- [ ] Database migrations tested
- [ ] Backup/restore procedures tested

### 🎯 Quick Wins (Easy Fixes)

1. **Add real-time price updates to frontend**
   - Connect existing WebSocket to chart component
   - Estimated: 1 hour

2. **Complete chart time range functionality**
   - Fetch different date ranges from API
   - Estimated: 2 hours

3. **Add loading spinners**
   - Show while fetching data
   - Estimated: 1 hour

4. **Improve error messages**
   - User-friendly error displays
   - Estimated: 2 hours

5. **Add more mock news headlines**
   - Diverse sentiment examples
   - Estimated: 30 minutes

### 💡 Development Tips

**When testing predictions:**
- First trigger data fetch: `POST /api/v1/data/fetch`
- Wait for data to populate
- Then generate prediction: `POST /api/v1/predict`

**When debugging:**
- Check Docker logs: `docker-compose logs -f`
- Backend logs show detailed errors
- Frontend errors in browser console (F12)

**When models won't train:**
- Need minimum 60 data points
- Check sequence_length configuration
- Verify data quality in database

**When frontend won't connect:**
- Verify backend is running
- Check CORS_ORIGINS in .env
- Ensure .env.local has correct API_URL

### 📊 Performance Metrics to Watch

**Current Benchmarks (Mock Data):**
- API health check: ~5ms
- Latest price fetch: ~20ms
- Prediction generation: ~50ms (without ML model)
- Historical data (30 days): ~30ms

**Expected with Real Models:**
- Prediction generation: 2-5 seconds
- Model training: 10-30 minutes
- Background task cycle: varies

### 🔄 Git Workflow

**Current branches:**
- `main`: Production-ready code
- `develop`: Development branch
- Feature branches: `feature/name`

**Before committing:**
```bash
# Run tests
cd backend && uv run pytest tests/

# Check linting
cd backend && uv run ruff check .

# Format code
cd backend && uv run black .
```

### 📞 Support & Resources

**Documentation:**
- SETUP.md - Detailed setup instructions
- README.md - Project overview
- API Docs - http://localhost:8000/docs

**Helpful Commands:**
```bash
# Quick restart
./stop.sh && ./start.sh

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Database check
docker-compose exec postgres psql -U postgres -d crude_oil_db

# Clear cache
docker-compose down -v && docker-compose up -d
```

---

**Last tested:** December 28, 2025  
**Next review:** After implementing Priority 1 items

---

## Current Development Status

**Phase 1-3:** ✅ Complete  
**Phase 4:** ⚠️ 90% Complete  
**Phase 5:** ⚠️ 70% Complete  
**Phase 6:** ⚠️ 80% Complete

**Overall:** 🟡 Alpha stage - functional but needs polish for production
