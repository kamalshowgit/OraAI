import io
import pandas as pd
import matplotlib.pyplot as plt

def generate_chart(data: list[list], columns: list[str], chart_type: str = "bar"):
    """
    Generates a chart from the given data and returns it as a PNG image.
    """
    df = pd.DataFrame(data, columns=columns)
    
    fig, ax = plt.subplots()
    
    if chart_type == "bar":
        df.plot(kind="bar", ax=ax)
    elif chart_type == "line":
        df.plot(kind="line", ax=ax)
    elif chart_type == "pie":
        df.plot(kind="pie", y=df.columns[1], ax=ax)
    else:
        raise ValueError("Unsupported chart type")
        
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    return buf
