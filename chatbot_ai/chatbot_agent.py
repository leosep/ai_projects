from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI

from chat_memory import get_memory
from document_loader import load_and_index_documents

def get_chain():
    retriever = load_and_index_documents().as_retriever()
    memory = get_memory()
    
    llm = ChatOpenAI(model_name="gpt-3.5-turbo")
    
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )
    return qa_chain
