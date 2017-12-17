import torch.nn as nn
import torch
import torch.cuda
from torch.autograd import Variable


class MatrixTree(nn.Module):
    """Implementation of the matrix-tree theorem for computing marginals
    of non-projective dependency parsing. This attention layer is used
    in the paper "Learning Structured Text Representations."

    qq

    .. mermaid::

       sequenceDiagram
          participant Alice
          participant Bob
          Alice->John: Hello John, how are you?
          loop Healthcheck
              John->John: Fight against hypochondria
          end
          Note right of John: Rational thoughts <br/>prevail...
          John-->Alice: Great!
          John->Bob: How about you?
          Bob-->John: Jolly good!
    """
    def __init__(self, eps=1e-5):
        self.eps = eps
        super(MatrixTree, self).__init__()

    def forward(self, input):
        laplacian = input.exp() + self.eps
        output = input.clone()
        for b in range(input.size(0)):
            lap = laplacian[b].masked_fill(
                Variable(torch.eye(input.size(1)).cuda().ne(0)), 0)
            lap = -lap + torch.diag(lap.sum(0))
            # store roots on diagonal
            lap[0] = input[b].diag().exp()
            inv_laplacian = lap.inverse()

            factor = inv_laplacian.diag().unsqueeze(1)\
                                         .expand_as(input[b]).transpose(0, 1)
            term1 = input[b].exp().mul(factor).clone()
            term2 = input[b].exp().mul(inv_laplacian.transpose(0, 1)).clone()
            term1[:, 0] = 0
            term2[0] = 0
            output[b] = term1 - term2
            roots_output = input[b].diag().exp().mul(
                inv_laplacian.transpose(0, 1)[0])
            output[b] = output[b] + torch.diag(roots_output)
        return output


if __name__ == "__main__":
    dtree = MatrixTree()
    q = torch.rand(1, 5, 5).cuda()
    marg = dtree.forward(Variable(q))
    print(marg.sum(1))
