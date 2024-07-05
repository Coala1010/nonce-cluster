import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split

batch_size = 256

# Generate randomly unlabeled data
num_samples = 10000000  # Adjust the number of samples as needed
X_unlabeled = np.random.randint(0, 128, size=(num_samples, 2))  # Generate random features within the range [0, 127]

# Convert NumPy arrays to PyTorch tensors
X_unlabeled_tensor = torch.tensor(X_unlabeled, dtype=torch.float32) / 127

# Load labeled data
labeled_data = np.load("database/mining_data.npy")
X_labeled = labeled_data[:, 1:]  # Features: b0, b3
y_labeled = labeled_data[:, 0]   # Labels: ASIC type

# Convert NumPy arrays to PyTorch tensors
X_labeled_tensor = torch.tensor(X_labeled, dtype=torch.float32) / 127
y_labeled_tensor = torch.tensor(y_labeled, dtype=torch.long)

print("labeled data size = {}".format(X_labeled_tensor.size()))

# Use CUDA if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Move tensors to GPU if available
X_unlabeled_tensor = X_unlabeled_tensor.to(device)
X_labeled_tensor = X_labeled_tensor.to(device)
y_labeled_tensor = y_labeled_tensor.to(device)

# Define a simple neural network model
class ClusterNN(nn.Module):
    def __init__(self):
        super(ClusterNN, self).__init__()
        self.fc1 = nn.Linear(2, 128)
        self.bn1 = nn.BatchNorm1d(128)
        self.dropout1 = nn.Dropout(0.2)  # Dropout with 20% probability
        self.fc2 = nn.Linear(128, 256)
        self.bn2 = nn.BatchNorm1d(256)
        self.dropout2 = nn.Dropout(0.2)  # Dropout with 20% probability
        self.fc3 = nn.Linear(256, 128)
        self.bn3 = nn.BatchNorm1d(128)
        self.dropout3 = nn.Dropout(0.2)  # Dropout with 20% probability
        self.fc4 = nn.Linear(128, 20)  

    def forward(self, x):
        x = torch.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)
        x = torch.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)
        x = torch.relu(self.bn3(self.fc3(x)))
        x = self.dropout3(x)
        x = torch.softmax(self.fc4(x), dim=1)
        return x
    
# Initialize the model and move to GPU if available
model = ClusterNN().to(device)

# Define loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop with pseudo-labeling
num_epochs = 30
for epoch in range(num_epochs):
    print(f"Epoch [{epoch+1}/{num_epochs}]")
    model.train()
    running_loss = 0.0

    # Train with labeled data
    for inputs, labels in DataLoader(TensorDataset(X_labeled_tensor, y_labeled_tensor), batch_size=batch_size, shuffle=True):
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * inputs.size(0)
    
    print(f"  Labeled data training loss: {running_loss / len(X_labeled_tensor)}")

    # Predict pseudo-labels for unlabeled data
    model.eval()
    with torch.no_grad():
        outputs_unlabeled = model(X_unlabeled_tensor)
        _, pseudo_labels = torch.max(outputs_unlabeled, 1)

    # Combine labeled and pseudo-labeled data
    combined_data = torch.cat((X_unlabeled_tensor, X_labeled_tensor), dim=0)
    combined_labels = torch.cat((pseudo_labels, y_labeled_tensor), dim=0)

    # Move combined data to GPU if available
    combined_data = combined_data.to(device)
    combined_labels = combined_labels.to(device)

    # Train with combined data
    running_loss = 0.0
    for inputs, labels in DataLoader(TensorDataset(combined_data, combined_labels), batch_size=batch_size, shuffle=True):
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * inputs.size(0)

    print(f"  Combined data training loss: {running_loss / (len(X_labeled_tensor) + len(X_unlabeled_tensor))}")

# Save the trained model
torch.save(model.state_dict(), 'ssl_model.pth')
