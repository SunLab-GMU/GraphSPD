import torch
from torch.nn import Linear, Sequential, ReLU
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, SAGPooling
from torch_geometric.nn import global_mean_pool, global_max_pool

class PGCN(torch.nn.Module): # PGCN
    def __init__(self, num_node_features):
        super(PGCN, self).__init__()
        torch.manual_seed(12345)
        self.conv1A = GCNConv(num_node_features, num_node_features)
        self.conv1B = GCNConv(num_node_features, num_node_features)
        self.conv1C = GCNConv(num_node_features, num_node_features)
        self.conv1D = GCNConv(num_node_features, num_node_features)
        self.conv2 = GCNConv(num_node_features * 4, num_node_features * 2)
        self.conv3 = GCNConv(num_node_features * 2, num_node_features)
        self.mlp = Sequential(
            Linear(num_node_features * 2, 8),
            ReLU(),
            Linear(8, 2)
        )

    def forward(self, x, edge_index, edge_attr, batch):
        # 1. Obtain node embeddings.
        # Layer 1
        xA = self.conv1A(x, edge_index, edge_attr[:, 0].contiguous()).relu()
        xB = self.conv1B(x, edge_index, edge_attr[:, 1].contiguous()).relu()
        xC = self.conv1C(x, edge_index, edge_attr[:, 2].contiguous()).relu()
        xD = self.conv1D(x, edge_index, edge_attr[:, 3].contiguous()).relu()
        # x = (xA + xB + xC + xD) / 4.0 # average
        x = torch.cat((xA, xB, xC, xD), dim=1)  # concat

        # Layer 2
        x = self.conv2(x, edge_index).relu()

        # Layer 3
        x = self.conv3(x, edge_index)

        # 2. Readout layer
        x = torch.cat([global_mean_pool(x, batch), global_max_pool(x, batch)], dim=1)  # [batch_size, hidden_channels]
        x = F.dropout(x, p=0.5, training=self.training)

        # 3. Apply a final classifier
        logits = self.mlp(x)

        return logits

class PGCN_g(torch.nn.Module): # PGCN_global
    def __init__(self, num_node_features):
        super(PGCN_g, self).__init__()
        torch.manual_seed(12345)
        self.conv1A = GCNConv(num_node_features, num_node_features)
        self.conv1B = GCNConv(num_node_features, num_node_features)
        self.conv1C = GCNConv(num_node_features, num_node_features)
        self.conv1D = GCNConv(num_node_features, num_node_features)
        self.conv2 = GCNConv(num_node_features * 4, num_node_features * 2)
        self.conv3 = GCNConv(num_node_features * 2, num_node_features)
        self.pool = SAGPooling(num_node_features * 7, ratio=0.5)
        self.mlp = Sequential(
            Linear(num_node_features * 14, 32),
            ReLU(),
            Linear(32, 8),
            ReLU(),
            Linear(8, 2)
        )

    def forward(self, x, edge_index, edge_attr, batch):
        # 1. Obtain node embeddings.
        # Layer 1
        xA = self.conv1A(x, edge_index, edge_attr[:, 0].contiguous()).relu()
        xB = self.conv1B(x, edge_index, edge_attr[:, 1].contiguous()).relu()
        xC = self.conv1C(x, edge_index, edge_attr[:, 2].contiguous()).relu()
        xD = self.conv1D(x, edge_index, edge_attr[:, 3].contiguous()).relu()
        # x = (xA + xB + xC + xD) / 4.0 # average
        gcn1 = torch.cat((xA, xB, xC, xD), dim=1) # concat

        # Layer 2
        gcn2 = self.conv2(gcn1, edge_index).relu()

        # Layer 3
        gcn3 = self.conv3(gcn2, edge_index)

        # 2. Readout layer
        gcn = torch.cat([gcn1, gcn2, gcn3], dim=1)
        pool, pool_index, _, pool_batch, _, _ = self.pool(gcn, edge_index, batch=batch)
        readout = torch.cat([global_mean_pool(pool, pool_batch), global_max_pool(pool, pool_batch)], dim=1)  # [batch_size, hidden_channels]

        # 3. Apply a final classifier
        logits = self.mlp(readout)

        return logits

class PGCN_h(torch.nn.Module): # PGCN_hierarchical
    def __init__(self, num_node_features):
        super(PGCN_h, self).__init__()
        torch.manual_seed(12345)
        self.conv1A = GCNConv(num_node_features, num_node_features)
        self.conv1B = GCNConv(num_node_features, num_node_features)
        self.conv1C = GCNConv(num_node_features, num_node_features)
        self.conv1D = GCNConv(num_node_features, num_node_features)
        self.pool1 = SAGPooling(num_node_features * 4, ratio=0.5)
        self.conv2 = GCNConv(num_node_features * 4, num_node_features * 2)
        self.pool2 = SAGPooling(num_node_features * 2, ratio=0.5)
        self.conv3 = GCNConv(num_node_features * 2, num_node_features)
        self.pool3 = SAGPooling(num_node_features, ratio=0.5)
        self.mlp = Sequential(
            Linear(num_node_features * 14, 32),
            ReLU(),
            Linear(32, 8),
            ReLU(),
            Linear(8, 2)
        )

    def forward(self, x, edge_index, edge_attr, batch):
        # 1. Obtain node embeddings.
        # Layer 1
        xA = self.conv1A(x, edge_index, edge_attr[:, 0].contiguous()).relu()
        xB = self.conv1B(x, edge_index, edge_attr[:, 1].contiguous()).relu()
        xC = self.conv1C(x, edge_index, edge_attr[:, 2].contiguous()).relu()
        xD = self.conv1D(x, edge_index, edge_attr[:, 3].contiguous()).relu()
        # x = (xA + xB + xC + xD) / 4.0 # average
        gcn1 = torch.cat((xA, xB, xC, xD), dim=1) # concat
        pool1, edge_index1, _, batch1, _, _ = self.pool1(gcn1, edge_index, batch=batch)
        global_pool1 = torch.cat([global_mean_pool(pool1, batch1), global_max_pool(pool1, batch1)], dim=1)

        # Layer 2
        gcn2 = self.conv2(pool1, edge_index1).relu()
        pool2, edge_index2, _, batch2, _, _ = self.pool2(gcn2, edge_index1, batch=batch1)
        global_pool2 = torch.cat([global_mean_pool(pool2, batch2), global_max_pool(pool2, batch2)], dim=1)

        # Layer 3
        gcn3 = self.conv3(pool2, edge_index2)
        pool3, edge_index3, _, batch3, _, _ = self.pool3(gcn3, edge_index2, batch=batch2)
        global_pool3 = torch.cat([global_mean_pool(pool3, batch3), global_max_pool(pool3, batch3)], dim=1)

        # 2. Readout layer
        readout = torch.cat([global_pool1, global_pool2, global_pool3], dim=1)  # [batch_size, hidden_channels]

        # 3. Apply a final classifier
        logits = self.mlp(readout)

        return logits

def PGCNTrain(model, trainloader, optimizer, criterion):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.train()

    lossTrain = 0
    for data in trainloader:  # Iterate in batches over the training dataset.
        optimizer.zero_grad()  # Clear gradients.
        data.to(device)
        out = model.forward(data.x, data.edge_index, data.edge_attr, data.batch)  # Perform a single forward pass.
        loss = criterion(out, data.y)  # Compute the loss.
        loss.backward()  # Derive gradients.
        optimizer.step()  # Update parameters based on gradients.
        # statistic.
        lossTrain += loss.item() * len(data.y)

    lossTrain /= len(trainloader.dataset)

    return model, lossTrain

def PGCNTest(model, loader):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    correct = 0
    preds = []
    labels = []
    for data in loader:  # Iterate in batches over the training/test dataset.
        data.to(device)
        out = model.forward(data.x, data.edge_index, data.edge_attr, data.batch)
        pred = out.argmax(dim=1)  # Use the class with highest probability.
        # statistic.
        correct += int((pred == data.y).sum())  # Check against ground-truth labels.
        preds.extend(pred.int().tolist())
        labels.extend(data.y.int().tolist())

    acc = correct / len(loader.dataset)  # Derive ratio of correct predictions.

    return acc, preds, labels