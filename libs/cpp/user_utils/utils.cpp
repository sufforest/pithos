#include "utils.h"
#include <sstream>
namespace user_utils {
    std::string GetWelcomeMessage(const std::string& name) {
        return "Welcome, " + name + "!";
    }
}
