import matplotlib.pyplot as plt

def main():

    plotShow = False

    # Plot how the elevation changes with aspect ratio for two different
    # xy_ratio values. The red line corresponds to xy_ratio=1.3, the green line
    # corresponds to xy_ratio=1.5, and the blue line corresponds to
    # xy_ratio=1.95.
    x = [0.5, 0.85, 1.0, 1.15, 1.5, 2, 3]
    y1 = [37, 37, 43, 49, 62, 80, 118]
    y2 = [32, 34, 39, 44, 56, 73, 108]
    y3 = [24, 28, 32, 37, 46, 61, 89]
    plt.plot(x, y1, "r-x", x, y2, "g-x", x, y3, "b-x")
    if plotShow is True:
        plt.show()

    # The elevation is linear with the aspect ratio above a certain
    # threshold. Identify the gradients of the three lines.
    grads = []
    grads.append((y1[-1] - y1[-2]) / (x[-1] - x[-2]))
    grads.append((y2[-1] - y2[-2]) / (x[-1] - x[-2]))
    grads.append((y3[-1] - y3[-2]) / (x[-1] - x[-2]))

    # Plot these gradients against the xy_ratio.
    z = [1.3, 1.5, 1.95]
    plt.plot(z, grads, "k-x")
    if plotShow is True:
        plt.show()

    # Find the gradient of these gradients. Is close to 2/3.
    print (z[1] - z[0]) / (grads[1] - grads[0])
    print (z[2] - z[1]) / (grads[2] - grads[1])

    # So what does this all mean? Good question. The relationship of elevation
    # with xy_ratio is linear (with a pretty constant gradient). Furthermore,
    # the ratio of elevation with aspect ratio is also linear.


if __name__ == "__main__":
    main()
