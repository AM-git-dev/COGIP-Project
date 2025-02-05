from fastapi import APIRouter, HTTPException
from config.database import get_connection
from pydantic import BaseModel, Field
from datetime import datetime, date, time
from fastapi_pagination import Page, add_pagination, paginate, Params
# from fastapi_pagination import settings

router = APIRouter()
add_pagination(router)

# settings.default_size = 10
# settings.max_size = 10
# settings.max_page = 10

class InvoicesVerify(BaseModel):
    ref : str = Field(min_length=2, max_length=50)
    id_company : int

class SearchInvoices(BaseModel):
    name: str = Field(min_length=2, max_length=50)

class DeleteInvoices(BaseModel):
    ref : str = Field(min_length=2, max_length=50)

class GetInvoice(BaseModel):
    ref : str = Field(min_length=2, max_length=50)

class GetAllInvoices(BaseModel):
    ref: str = Field(min_length=2, max_length=50)
    created_at: datetime = Field(default_factory=datetime.now)
    company_name: str = Field(min_length=2, max_length=50)

    class Config:
        from_attribute = True


@router.get("/get_invoice")
async def get_invoice(ref_invoice: GetInvoice):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT invoices.ref, companies.name AS company_name, invoices.created_at FROM invoices LEFT JOIN companies ON invoices.id_company = companies.id WHERE invoices.ref = %s"
        values = (ref_invoice.ref,)

        cursor.execute(query, values)

        get_one_invoice = cursor.fetchone()

        cursor.close()
        conn.close()

        return get_one_invoice

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_all_invoices", response_model=Page[GetAllInvoices])
async def get_invoices(params: Params = Params()):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT invoices.ref, invoices.created_at, companies.name AS company_name FROM invoices LEFT JOIN companies ON invoices.id_company = companies.id LIMIT 10")

        get_invoice = cursor.fetchall()

        cursor.close()
        conn.close()

        return paginate(get_invoice, params)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search_invoice")
async def search_invoices(search: SearchInvoices):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT invoices.ref, companies.name, invoices.created_at FROM invoices LEFT JOIN companies ON invoices.id_company = companies.id WHERE companies.name = %s"
        values = (search.name, )

        cursor.execute(query, values)
        search_invoice = cursor.fetchall()

        cursor.close()
        conn.close()

        return search_invoice

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_last_invoices")
async def get_last_invoices():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT invoices.ref, invoices.created_at, companies.name FROM invoices LEFT JOIN companies ON invoices.id_company = companies.id ORDER BY created_at DESC LIMIT 5")

        get_last_invoice = cursor.fetchall()

        cursor.close()
        conn.close()

        return get_last_invoice

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_last_invoices_company/{company_name}")
async def get_last_invoices_company(company_name : str):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT invoices.ref, invoices.created_at, companies.name AS company_name FROM invoices LEFT JOIN companies ON invoices.id_company = companies.id WHERE companies.name = %s ORDER BY created_at DESC LIMIT 5"
        values = (company_name,)

        cursor.execute(query, values)

        get_last_invoice_company = cursor.fetchall()

        cursor.close()
        conn.close()

        return get_last_invoice_company

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_invoice")
async def create_invoices(invoices: InvoicesVerify ):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "INSERT INTO invoices (ref, id_company) VALUES (%s, %s)"
        values = (invoices.ref, invoices.id_company)

        cursor.execute(query, values)
        conn.commit()

        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM invoices WHERE id_company = %s", (new_id,))
        create_invoice = cursor.fetchone()

        cursor.close()
        conn.close()

        return create_invoice

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update_invoice/{invoice_id}")
async def update_invoices(invoice_id: int, invoices: InvoicesVerify ):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM invoices WHERE id = %s", (invoice_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Facture non trouvé")

        query = "UPDATE invoices SET ref = %s WHERE id = %s"
        values = (invoices.ref, invoice_id)

        cursor.execute(query, values)
        conn.commit()

        cursor.execute ("SELECT * FROM invoices WHERE id = %s", (invoice_id,))
        update_invoice = cursor.fetchone()

        cursor.close()
        conn.close()

        return update_invoice

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_invoice/{invoice_id}")
async def delete_invoice(invoice_id: int, invoices: DeleteInvoices):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM invoices WHERE id = %s", (invoice_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Contact non trouvé")

        query = "DELETE FROM invoices WHERE ref = %s"
        values = (invoices.ref,)

        cursor.execute(query, values)
        conn.commit()

        cursor.execute("SELECT * FROM invoices")

        delete_invoices = cursor.fetchall()

        cursor.close()
        conn.close()

        return delete_invoices

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))