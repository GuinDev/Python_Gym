import streamlit as st
import pandas as pd

st.set_page_config( 
    page_title="Gerenciar Pagamentos",)

st.write("# Gerenciar Pagamentos")

df=pd.DataFrame({
    'ID': [1, 2,],
    'Nome': ['joao silva','maria oliveira'],
    'valor': [150.00, 200.00],
    'data': ['2024-01-15', '2024-01-20'],
    'Estado': ['pago', 'pendente'],
    })

st.dataframe(df.set_index('ID'))

conn = st.connection("postgresql", type="sql")

# Perform query.
df = conn.query('SELECT * FROM pagamentos;', ttl="10m")

# Print results.
for row in df.itertuples():
    st.write(
        f"ID: {row.ID}, Nome: {row.Nome}, Valor: {row.valor}, Data: {row.data}, Estado: {row.Estado}"
    )
