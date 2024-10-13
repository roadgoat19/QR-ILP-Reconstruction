import pandas as pd
from plotnine import ggplot, aes, geom_point, theme, labs


# Use regex to define a complex delimiter
df = pd.read_csv('output.csv', delimiter=r',(?!\s)', engine='python')
print(df.head())


print(df.head(10))

# Step 2: Parse the coordinates from the Point column
def extract_coordinates(point):
    x, y = point.strip('()').split(', ')
    return int(x), int(y)

# Apply the function to extract x and y
df[['x', 'y']] = df['Point'].apply(lambda p: pd.Series(extract_coordinates(p)))

# Step 3: Create the plot using plotnine
plot = (
    ggplot(df, aes('x', 'y', size='Accuracy')) +  # Position points at (x, y) and scale size by Accuracy
    geom_point(alpha=0.6, color='blue') +  # Adjust point transparency and color
    labs(title='QR Code Points Visualization', x='X Coordinate', y='Y Coordinate', size='Accuracy') + 
    theme(legend_position='right')  # Adjust legend position
)

# Display the plot
print(plot)

# Optionally, save the plot to a file
plot.save('qr_code_plot.png', width=10, height=10, dpi=300)
