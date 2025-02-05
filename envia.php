<?php
    // Verifica se a requisição foi feita via POST
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        // Obtém os dados do formulário e evita vulnerabilidades
        $nome = addslashes($_POST['nome'] ?? '');
        $email = addslashes($_POST['email'] ?? '');
        $telefone = addslashes($_POST['telefone'] ?? '');

        // Verifica se os campos necessários foram preenchidos
        if (!empty($nome) && !empty($email) && !empty($telefone)) {
            $para = "vitor.bferreira118@gmail.com";
            $assunto = "Mensagem do site";

            $corpo = "Nome: " . $nome . "\n" .
                     "E-mail: " . $email . "\n" .
                     "Telefone: " . $telefone;

            $cabecalho = "From: vitinhobferreira10@gmail.com" . "\r\n" .
                         "Reply-To: " . $email . "\r\n" .
                         "X-Mailer: PHP/" . phpversion();

            // Envia o e-mail
            if (mail($para, $assunto, $corpo, $cabecalho)) {
                echo "E-mail enviado com sucesso!";
            } else {
                echo "Houve um erro ao enviar o e-mail.";
            }
        } else {
            echo "Por favor, preencha todos os campos.";
        }
    } else {
        echo "Método de requisição inválido.";
    }
?>
