# Task Manager API

Görev ve proje yönetimi REST API'si. Kullanıcılar projeler oluşturabilir, görevler ekleyebilir, öncelik ve durum belirleyebilir, deadline takibi yapabilir.

## Özellikler

- JWT tabanlı kimlik doğrulama (kayıt/giriş)
- Proje oluşturma ve yönetimi
- Görev CRUD (oluşturma, okuma, güncelleme, silme)
- Öncelik seviyeleri: low, medium, high
- Durum takibi: todo, in_progress, done
- Deadline ve süresi geçmiş görev filtreleme
- Duruma, önceliğe, projeye göre filtreleme
- Başlıkta arama
- Pagination (sayfalama)
- Kullanıcı izolasyonu (herkes sadece kendi verilerini görür)

## Teknolojiler

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **SQLite** - Veritabanı
- **JWT** - Kimlik doğrulama
- **Bcrypt** - Şifre hashleme
- **Pytest** - Test framework

## Kurulum

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
uvicorn app.main:app --reload
```

API dokümantasyonu: http://localhost:8000/docs

## Test

```bash
pytest tests/ -v
```

## API Endpoint'leri

### Auth
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | /auth/register | Kayıt ol |
| POST | /auth/login | Giriş yap |

### Projeler
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | /projects/ | Proje oluştur |
| GET | /projects/ | Projeleri listele |
| GET | /projects/{id} | Proje detayı |
| PUT | /projects/{id} | Proje güncelle |
| DELETE | /projects/{id} | Proje sil |

### Görevler
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | /tasks/ | Görev oluştur |
| GET | /tasks/ | Görevleri listele (filtreleme destekli) |
| GET | /tasks/{id} | Görev detayı |
| PUT | /tasks/{id} | Görev güncelle |
| DELETE | /tasks/{id} | Görev sil |

### Filtreleme Parametreleri
- `status` - todo, in_progress, done
- `priority` - low, medium, high
- `project_id` - Projeye göre filtrele
- `search` - Başlıkta ara
- `overdue` - Süresi geçmiş görevler
- `skip` / `limit` - Sayfalama
